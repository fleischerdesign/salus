import json
import os
import subprocess
import tempfile

import pytest
from fastapi import FastAPI


@pytest.fixture(scope="session")
def _cached_app() -> FastAPI:
    from salus.main import create_app

    return create_app()


@pytest.fixture(scope="session")
def openapi_spec(_cached_app: FastAPI) -> dict:
    return _cached_app.openapi()


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

    def test_openapi_has_paths(self, openapi_spec: dict):
        assert "paths" in openapi_spec
        assert len(openapi_spec["paths"]) > 0

    def test_openapi_has_components(self, openapi_spec: dict):
        assert "components" in openapi_spec
        assert "schemas" in openapi_spec["components"]
        assert len(openapi_spec["components"]["schemas"]) > 0

    def test_openapi_no_duplicate_operation_ids(self, openapi_spec: dict):
        ids: list[str] = []
        for _path, methods in openapi_spec["paths"].items():
            for method in methods.values():
                if "operationId" in method:
                    ids.append(method["operationId"])
        duplicates = [oid for oid in ids if ids.count(oid) > 1]
        assert not duplicates, f"Duplicate operationIds: {set(duplicates)}"

    def test_openapi_asymmetric_share_id_is_string(self, openapi_spec: dict):
        share_schema = openapi_spec["components"]["schemas"]["AsymmetricShareResponse"]
        id_prop = share_schema["properties"]["id"]
        assert id_prop["type"] == "string", (
            f"Expected AsymmetricShareResponse.id to be string, got {id_prop['type']}"
        )


class TestSchemaDrift:
    """Detect drift between backend OpenAPI spec and frontend schema.d.ts.

    Requires openapi-typescript CLI installed in frontend/node_modules.
    """

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
def regenerated_schema_path(openapi_spec: dict):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(openapi_spec, f)
        openapi_path = f.name

    output_path = tempfile.NamedTemporaryFile(suffix=".d.ts", delete=False).name
    _regenerate_schema_dts(openapi_path, output_path)
    yield output_path
    os.unlink(openapi_path)
    os.unlink(output_path)
