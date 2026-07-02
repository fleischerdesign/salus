import json
import logging
import importlib.util
import shutil
import zipfile
import io
from pathlib import Path
from datetime import datetime, timezone

from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.plugin.context import PluginContext
from salus.services.plugin.hooks import HookRegistry
from salus.services.plugin.base import BasePlugin

logger = logging.getLogger("salus.plugin.manager")


class PluginManager:
    def __init__(self, plugins_dir: str | Path, uow: IUnitOfWork) -> None:
        self.plugins_dir = Path(plugins_dir)
        self.uow = uow
        self.registry = HookRegistry()
        self.loaded_plugins: dict[str, BasePlugin] = {}

    def _get_enabled_plugin_ids(self) -> set[str]:
        with self.uow:
            config = self.uow.system_configs.get_by_key("enabled_plugins")
            if not config:
                # First run: enable all discovered plugins on disk by default
                all_ids = set()
                if self.plugins_dir.exists():
                    for path in self.plugins_dir.iterdir():
                        if path.is_dir() and not path.name.startswith("__"):
                            manifest_path = path / "manifest.json"
                            if manifest_path.exists():
                                try:
                                    with open(manifest_path, "r", encoding="utf-8") as f:
                                        m = json.load(f)
                                        if m.get("id"):
                                            all_ids.add(m["id"])
                                except Exception:
                                    pass
                self.uow.system_configs.upsert("enabled_plugins", json.dumps(list(all_ids)))
                return all_ids
            try:
                return set(json.loads(config.value))
            except Exception:
                return set()

    def discover_and_load_all(self) -> None:
        """Scans the plugins directory and loads plugins that are enabled in config."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist. Creating it.")
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return

        enabled_ids = self._get_enabled_plugin_ids()

        for path in self.plugins_dir.iterdir():
            if path.is_dir() and not path.name.startswith("__"):
                manifest_path = path / "manifest.json"
                if not manifest_path.exists():
                    logger.debug(f"Skipping directory {path.name}: manifest.json not found")
                    continue

                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    plugin_id = manifest.get("id")
                    if plugin_id and plugin_id in enabled_ids:
                        self._load_plugin(path, manifest_path)
                    else:
                        logger.info(f"Plugin {plugin_id} is disabled. Skipping load.")
                except Exception as e:
                    logger.error(f"Failed to load plugin from {path.name}: {str(e)}", exc_info=True)

    def get_discovered_plugins(self) -> list[dict]:
        """Scans disk to find all plugins and checks database for active status."""
        discovered = []
        enabled_ids = self._get_enabled_plugin_ids()
        
        if not self.plugins_dir.exists():
            return []
            
        for path in self.plugins_dir.iterdir():
            if path.is_dir() and not path.name.startswith("__"):
                manifest_path = path / "manifest.json"
                if not manifest_path.exists():
                    continue
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    plugin_id = manifest.get("id")
                    if plugin_id:
                        manifest["enabled"] = plugin_id in enabled_ids
                        manifest["loaded"] = plugin_id in self.loaded_plugins
                        discovered.append(manifest)
                except Exception:
                    pass
        return discovered

    def toggle_plugin(self, plugin_id: str, enable: bool) -> None:
        """Enables/disables a plugin in the database and updates memory registration."""
        enabled_ids = self._get_enabled_plugin_ids()
        if enable:
            enabled_ids.add(plugin_id)
        else:
            enabled_ids.discard(plugin_id)
            
        with self.uow:
            self.uow.system_configs.upsert("enabled_plugins", json.dumps(list(enabled_ids)))
            
        # Dynamically load or unload in memory
        if enable:
            if plugin_id not in self.loaded_plugins:
                for path in self.plugins_dir.iterdir():
                    if path.is_dir() and not path.name.startswith("__"):
                        manifest_path = path / "manifest.json"
                        if manifest_path.exists():
                            try:
                                with open(manifest_path, "r", encoding="utf-8") as f:
                                    m = json.load(f)
                                if m.get("id") == plugin_id:
                                    self._load_plugin(path, manifest_path)
                                    break
                            except Exception:
                                pass
        else:
            if plugin_id in self.loaded_plugins:
                plugin_instance = self.loaded_plugins[plugin_id]
                try:
                    plugin_instance.on_unload()
                except Exception as e:
                    logger.error(f"Error calling on_unload for plugin {plugin_id}: {e}")
                self.registry.unregister(plugin_instance)
                del self.loaded_plugins[plugin_id]
                logger.info(f"Dynamically unloaded plugin {plugin_id}")

    def install_plugin(self, zip_file_bytes: bytes) -> str:
        """Securely extracts a plugin ZIP file to the plugins directory."""
        temp_dir = self.plugins_dir / f"temp_install_{int(datetime.now(timezone.utc).timestamp())}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_file_bytes)) as z:
                # Security Check: path traversal / zip slip
                for name in z.namelist():
                    target_path = (temp_dir / name).resolve()
                    if temp_dir not in target_path.parents and target_path != temp_dir:
                        raise ValueError(f"Security validation failed: invalid path in zip file: {name}")
                
                z.extractall(temp_dir)
                
            manifest_path = temp_dir / "manifest.json"
            src_dir = temp_dir
            
            if not manifest_path.exists():
                # Check if there is exactly one subfolder containing manifest.json
                subdirs = [p for p in temp_dir.iterdir() if p.is_dir()]
                if len(subdirs) == 1 and (subdirs[0] / "manifest.json").exists():
                    manifest_path = subdirs[0] / "manifest.json"
                    src_dir = subdirs[0]
                else:
                    raise ValueError("manifest.json not found in ZIP archive root or single subdirectory")
                    
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                
            plugin_id = manifest.get("id")
            if not plugin_id:
                raise ValueError("Plugin manifest missing 'id'")
                
            final_dir = self.plugins_dir / plugin_id
            if final_dir.exists():
                self.toggle_plugin(plugin_id, enable=False)
                shutil.rmtree(final_dir)
                
            shutil.copytree(src_dir, final_dir)
            logger.info(f"Successfully installed plugin files to {final_dir}")
            
            self.toggle_plugin(plugin_id, enable=True)
            return plugin_id
            
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def uninstall_plugin(self, plugin_id: str) -> None:
        """Disables the plugin, unloads it, and removes its directory from disk."""
        self.toggle_plugin(plugin_id, enable=False)
        
        enabled_ids = self._get_enabled_plugin_ids()
        enabled_ids.discard(plugin_id)
        with self.uow:
            self.uow.system_configs.upsert("enabled_plugins", json.dumps(list(enabled_ids)))
            
        final_dir = self.plugins_dir / plugin_id
        if final_dir.exists() and final_dir.is_dir():
            shutil.rmtree(final_dir)
            logger.info(f"Successfully deleted plugin directory: {final_dir}")

    def _load_plugin(self, plugin_dir: Path, manifest_path: Path) -> None:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        plugin_id = manifest.get("id")
        entrypoint = manifest.get("entrypoint")

        if not plugin_id or not entrypoint:
            raise ValueError("Plugin manifest missing required 'id' or 'entrypoint' fields")

        logger.info(f"Loading plugin: {plugin_id} (version {manifest.get('version', '0.0.0')})")

        parts = entrypoint.split(".")
        if len(parts) != 2:
            raise ValueError(f"Invalid entrypoint format: '{entrypoint}'. Expected 'module_name.ClassName'")
        module_name, class_name = parts

        module_file = plugin_dir / f"{module_name}.py"
        if not module_file.exists():
            raise FileNotFoundError(f"Entrypoint module file '{module_file}' not found")

        spec = importlib.util.spec_from_file_location(f"salus.plugins.{plugin_id}.{module_name}", module_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for module {module_file}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin_class = getattr(module, class_name, None)
        if plugin_class is None:
            raise AttributeError(f"Class '{class_name}' not found in module '{module_name}'")

        if not issubclass(plugin_class, BasePlugin):
            raise TypeError(f"Plugin class '{class_name}' must inherit from salus.services.plugin.base.BasePlugin")

        context = PluginContext(self.uow, manifest)
        plugin_instance = plugin_class(context)

        plugin_instance.initialize()
        plugin_instance.on_load()

        self.registry.register(plugin_instance)

        self.loaded_plugins[plugin_id] = plugin_instance
        logger.info(f"Successfully loaded and registered plugin: {plugin_id}")

    def unload_all(self) -> None:
        for plugin_id, plugin in list(self.loaded_plugins.items()):
            try:
                plugin.on_unload()
                logger.info(f"Unloaded plugin: {plugin_id}")
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_id}: {str(e)}", exc_info=True)
        self.loaded_plugins.clear()
        self.registry = HookRegistry()
