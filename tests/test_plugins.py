import pytest
import json
from pathlib import Path
from sqlmodel import Session

from salus.exceptions import ForbiddenError
from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models.user import User as UserModel
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.plugin import BasePlugin, PluginContext, PluginManager
from salus.services.plugin.hooks import HookRegistry
from salus.services.parser import FlexiblePayloadParser, register_parser
from salus.services.webhook_ingestion import WebhookIngestionService
from salus.services.insight.service import InsightService


# Helper plugin subclass to test permissions sandbox
class RestrictedPlugin(BasePlugin):
    pass


def test_plugin_context_permissions(session: Session):
    uow = SqlUnitOfWork(session)
    
    # 1. Manifest without measurements:read permission
    manifest_restricted = {
        "id": "restricted",
        "permissions": []
    }
    context_restricted = PluginContext(uow, manifest_restricted)
    
    with pytest.raises(ForbiddenError) as exc_info:
        context_restricted.get_measurements(user_id=1, data_type="steps")
    assert "Permission denied: Plugin 'restricted' lacks required permission 'measurements:read'" in str(exc_info.value)

    # 2. Manifest with measurements:read permission
    manifest_allowed = {
        "id": "allowed",
        "permissions": ["measurements:read"]
    }
    context_allowed = PluginContext(uow, manifest_allowed)
    # This should not raise ForbiddenError (even if empty results return)
    res = context_allowed.get_measurements(user_id=1, data_type="steps")
    assert isinstance(res, list)


def test_plugin_discovery_and_lifecycle(session: Session):
    uow = SqlUnitOfWork(session)
    # The actual demo plugin should be discovered
    plugins_dir = Path("src/salus/plugins")
    manager = PluginManager(plugins_dir, uow)
    manager.discover_and_load_all()
    
    assert "demo_plugin" in manager.loaded_plugins
    plugin = manager.loaded_plugins["demo_plugin"]
    assert isinstance(plugin, BasePlugin)
    
    # Verify hooks are registered
    registry = manager.registry
    assert len(registry.parsers) > 0
    assert len(registry.api_routers) > 0
    assert len(registry.event_subscribers) > 0
    assert len(registry.ai_coach_contexts) > 0
    assert len(registry.translations) > 0

    # Unload
    manager.unload_all()
    assert len(manager.loaded_plugins) == 0
    assert len(manager.registry.parsers) == 0


def test_flexible_payload_parser_with_plugin_parser(session: Session):
    uow = SqlUnitOfWork(session)
    plugins_dir = Path("src/salus/plugins")
    manager = PluginManager(plugins_dir, uow)
    manager.discover_and_load_all()

    # Register the demo parser globally
    for parser_hook in manager.registry.parsers:
        register_parser(parser_hook)

    fpp = FlexiblePayloadParser()
    payload = {"source": "demo", "value": 120.0}
    
    assert fpp.can_handle(payload)
    records = fpp.parse(payload)
    assert len(records) == 1
    assert records[0].source == "demo"
    assert records[0].data_type == "demo_metric"
    assert records[0].value_numeric == 120.0


def test_event_subscriber_hook_firing(session: Session):
    registry = HookRegistry()

    # Create a mock subscriber that logs calls
    class MockSubscriber:
        def __init__(self):
            self.created_measurements = []
            self.achieved_goals = []

        def on_measurement_created(self, measurement: Measurement) -> None:
            self.created_measurements.append(measurement)

        def on_goal_achieved(self, goal: Goal) -> None:
            self.achieved_goals.append(goal)

    mock_sub = MockSubscriber()
    registry.register(mock_sub)

    # Ingest event test via WebhookIngestionService
    parser = FlexiblePayloadParser()
    # Resolve repositories
    from salus.repositories.measurement import MeasurementRepository
    from salus.repositories.metric_type import MetricTypeRepository
    from salus.services.metric_type_mapping import MetricTypeMappingService
    
    m_repo = MeasurementRepository(session, registry=registry)
    mt_repo = MetricTypeRepository(session)
    mapping_svc = MetricTypeMappingService(mt_repo)
    
    ingest_svc = WebhookIngestionService(parser, m_repo, mapping_svc, registry=registry)

    user = UserModel(username="testhook", password_hash="hash")
    session.add(user)
    session.commit()

    payload = [{"type": "steps", "value": 8500.0, "source": "flat_array", "startTime": "2026-07-02T10:00:00Z"}]
    ingest_svc.ingest(payload, user_id=user.id)
    
    assert len(mock_sub.created_measurements) == 1
    assert mock_sub.created_measurements[0].value_numeric == 8500.0


def test_ingestion_interceptor_hook(session: Session):
    registry = HookRegistry()

    class DoublingInterceptor:
        def intercept(self, measurements: list[Measurement]) -> list[Measurement]:
            for m in measurements:
                if m.value_numeric is not None:
                    m.value_numeric = m.value_numeric * 2
            return measurements

    registry.register(DoublingInterceptor())

    parser = FlexiblePayloadParser()
    from salus.repositories.measurement import MeasurementRepository
    from salus.repositories.metric_type import MetricTypeRepository
    from salus.services.metric_type_mapping import MetricTypeMappingService
    
    m_repo = MeasurementRepository(session, registry=registry)
    mt_repo = MetricTypeRepository(session)
    mapping_svc = MetricTypeMappingService(mt_repo)
    
    ingest_svc = WebhookIngestionService(parser, m_repo, mapping_svc, registry=registry)
    
    user = UserModel(username="testintc", password_hash="hash")
    session.add(user)
    session.commit()

    payload = [{"type": "steps", "value": 5000.0, "source": "flat_array", "startTime": "2026-07-02T10:00:00Z"}]
    ingest_svc.ingest(payload, user_id=user.id)
    
    # Check database records
    db_records = m_repo.find_all(user_id=user.id, data_types=["steps"])
    assert len(db_records) == 1
    assert db_records[0].value_numeric == 10000.0  # Doubled from 5000.0


def test_metric_synthesizer_hook(session: Session):
    registry = HookRegistry()

    class HeartRateAverageSynthesizer:
        def get_synthetic_metric_name(self) -> str:
            return "hr_avg_synth"

        def synthesize(self, user_id: int, measurements: list[Measurement]) -> list[Measurement]:
            # Create a synthetic measurement based on current metrics
            from datetime import datetime, timezone
            return [Measurement(
                user_id=user_id,
                data_type="hr_avg_synth",
                source="synthesizer",
                value_numeric=72.5,
                start_time=datetime.now(timezone.utc),
                external_id="synth-hr-1"
            )]

    registry.register(HeartRateAverageSynthesizer())
    from salus.repositories.measurement import MeasurementRepository
    m_repo = MeasurementRepository(session, registry=registry)
    
    # Querying should trigger synthesizer and return the synthetic record
    res = m_repo.find_all(user_id=1, data_types=["hr_avg_synth"])
    assert len(res) == 1
    assert res[0].data_type == "hr_avg_synth"
    assert res[0].value_numeric == 72.5


def test_ai_coach_context_hook_injection(session: Session):
    uow = SqlUnitOfWork(session)
    registry = HookRegistry()

    class ExtraInsightContext:
        def get_additional_prompt_context(self, user_id: str, date_str: str) -> str:
            return "PLUGINS_ROCK"

    registry.register(ExtraInsightContext())

    class DummyLlmProvider:
        def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
            # We want to assert that the prompt contains the hook output
            assert "PLUGINS_ROCK" in prompt
            return "Daily insight content."

    # Seed some user info to satisfy service loading
    from salus.models.user import User as UserModel
    
    with uow:
        user = UserModel(username="testcoach", password_hash="hash")
        uow.session.add(user)
        uow.commit()
        user_id = user.id
        assert user_id is not None

    insight_svc = InsightService(
        uow=uow,
        provider=DummyLlmProvider(),
        model="dummy_model",
        registry=registry
    )

    insight_svc.generate_daily_insight(user_id=user_id, date_str="2026-07-02")


def test_admin_plugin_lifecycle_toggling_and_zip(session: Session, tmp_path: Path):
    uow = SqlUnitOfWork(session)
    
    # Create a mock plugins folder
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    
    # 1. Create a dummy plugin on disk
    dummy_plugin_dir = plugins_dir / "my_test_plugin"
    dummy_plugin_dir.mkdir()
    
    manifest = {
        "id": "my_test_plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "entrypoint": "main.MyTestPlugin",
        "permissions": []
    }
    with open(dummy_plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)
        
    code = """
from salus.services.plugin import BasePlugin
class MyTestPlugin(BasePlugin):
    def on_load(self):
        pass
    def on_unload(self):
        pass
"""
    with open(dummy_plugin_dir / "main.py", "w") as f:
        f.write(code)
        
    manager = PluginManager(plugins_dir, uow)
    
    # Load discovered - should be enabled by default on first run
    discovered = manager.get_discovered_plugins()
    assert len(discovered) == 1
    assert discovered[0]["id"] == "my_test_plugin"
    assert discovered[0]["enabled"] is True
    
    # Perform load
    manager.discover_and_load_all()
    assert "my_test_plugin" in manager.loaded_plugins
    
    # Toggle it off
    manager.toggle_plugin("my_test_plugin", enable=False)
    assert "my_test_plugin" not in manager.loaded_plugins
    discovered = manager.get_discovered_plugins()
    assert discovered[0]["enabled"] is False
    
    # Toggle it on
    manager.toggle_plugin("my_test_plugin", enable=True)
    assert "my_test_plugin" in manager.loaded_plugins
    discovered = manager.get_discovered_plugins()
    assert discovered[0]["enabled"] is True
    
    # 2. Test ZIP installation
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("manifest.json", json.dumps({
            "id": "zipped_plugin",
            "name": "Zipped Plugin",
            "version": "2.0.0",
            "entrypoint": "main.ZippedPlugin",
            "permissions": []
        }))
        zip_file.writestr("main.py", """
from salus.services.plugin import BasePlugin
class ZippedPlugin(BasePlugin):
    pass
""")
        
    zip_bytes = zip_buffer.getvalue()
    
    # Install ZIP plugin
    plugin_id = manager.install_plugin(zip_bytes)
    assert plugin_id == "zipped_plugin"
    assert (plugins_dir / "zipped_plugin" / "manifest.json").exists()
    assert "zipped_plugin" in manager.loaded_plugins
    
    # 3. Test path traversal / zip-slip prevention
    bad_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(bad_zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("../bad_file.txt", "malicious content")
        
    bad_zip_bytes = bad_zip_buffer.getvalue()
    with pytest.raises(ValueError) as exc_info:
        manager.install_plugin(bad_zip_bytes)
    assert "Security validation failed: invalid path in zip file" in str(exc_info.value)
    
    # 4. Uninstall plugin
    manager.uninstall_plugin("zipped_plugin")
    assert "zipped_plugin" not in manager.loaded_plugins
    assert not (plugins_dir / "zipped_plugin").exists()
