import json
import os
import subprocess
import tempfile

import pytest


def _openapi_json() -> dict:
    from salus.main import create_app
    app = create_app()
    return app.openapi()


def _regenerate_schema_dts(openapi_path: str, output_path: str) -> None:
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    cli = os.path.join(frontend_dir, "node_modules", ".bin", "openapi-typescript")
    result = subprocess.run(
        [cli, openapi_path, "-o", output_path, "--alphabetize"],
        capture_output=True, text=True, cwd=frontend_dir,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"openapi-typescript failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestOpenAPIConsistency:
    """Ensure the OpenAPI spec is internally consistent."""

    def test_openapi_has_paths(self):
        spec = _openapi_json()
        assert "paths" in spec
        assert len(spec["paths"]) > 0

    def test_openapi_has_components(self):
        spec = _openapi_json()
        assert "components" in spec
        assert "schemas" in spec["components"]
        assert len(spec["components"]["schemas"]) > 0

    def test_openapi_no_duplicate_operation_ids(self):
        spec = _openapi_json()
        ids: list[str] = []
        for path, methods in spec["paths"].items():
            for method in methods.values():
                if "operationId" in method:
                    ids.append(method["operationId"])
        duplicates = [oid for oid in ids if ids.count(oid) > 1]
        assert not duplicates, f"Duplicate operationIds: {set(duplicates)}"

    def test_openapi_asymmetric_share_id_is_string(self):
        spec = _openapi_json()
        share_schema = spec["components"]["schemas"]["AsymmetricShareResponse"]
        id_prop = share_schema["properties"]["id"]
        assert id_prop["type"] == "string", (
            f"Expected AsymmetricShareResponse.id to be string, got {id_prop['type']}"
        )


class TestSchemaDrift:
    """Detect drift between backend OpenAPI spec and frontend schema.d.ts."""

    def test_regenerated_matches_committed(self, regenerated_schema_path: str):
        committed_path = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "src", "lib", "api", "schema.d.ts"
        )
        with open(regenerated_schema_path) as f:
            regenerated = f.read()
        with open(committed_path) as f:
            committed = f.read()

        assert regenerated == committed, (
            "schema.d.ts is out of sync with the backend OpenAPI spec. "
            "Run 'npm run gen-schema' in the frontend/ directory to regenerate."
        )


@pytest.fixture(scope="class")
def regenerated_schema_path():
    spec = _openapi_json()
    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False, mode="w"
    ) as f:
        json.dump(spec, f)
        openapi_path = f.name

    output_path = tempfile.mktemp(suffix=".d.ts")
    _regenerate_schema_dts(openapi_path, output_path)
    yield output_path
    os.unlink(openapi_path)
    os.unlink(output_path)

    def test_regenerated_matches_committed(self, regenerated_schema_path: str):
        committed_path = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "src", "lib", "api", "schema.d.ts"
        )
        with open(regenerated_schema_path) as f:
            regenerated = f.read()
        with open(committed_path) as f:
            committed = f.read()

        assert regenerated == committed, (
            "schema.d.ts is out of sync with the backend OpenAPI spec. "
            "Run 'npm run gen-schema' in the frontend/ directory to regenerate."
        )
