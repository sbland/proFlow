"""Tests for the Flask adapter that serves the compiled process webview."""

import json
import tarfile
import zipfile
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

from proflow.analysis.webview.run_app import create_app

FRONTEND_DIRECTORY = Path("proflow/analysis/webview/static/force/frontend-dist")


def frontend_asset_paths() -> set[str]:
    """Return repository-relative paths for all generated frontend assets."""
    return {path.as_posix() for path in FRONTEND_DIRECTORY.rglob("*") if path.is_file()}


def test_root_serves_compiled_frontend() -> None:
    """The root route serves the generated frontend entry point."""
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Process Network" in response.data
    assert b"/assets/" in response.data


def test_frontend_assets_are_served() -> None:
    """The Flask adapter serves generated JavaScript and stylesheet assets."""
    client = create_app().test_client()
    html = client.get("/").get_data(as_text=True)
    asset_path = html.split('src="', 1)[1].split('"', 1)[0]

    response = client.get(asset_path)

    assert response.status_code == 200
    assert response.mimetype == "text/javascript"
    assert response.data


def test_data_route_returns_graph_json(tmp_path) -> None:
    """The data route returns the configured graph JSON document."""
    graph_data = {"nodes": [], "links": []}
    data_file = tmp_path / "graph.json"
    data_file.write_text(json.dumps(graph_data), encoding="utf-8")
    client = create_app(datalocation=data_file).test_client()

    response = client.get("/data")

    assert response.status_code == 200
    assert response.get_json() == graph_data


def test_data_route_reports_missing_file(tmp_path) -> None:
    """The data route reports a missing graph file as a not-found response."""
    client = create_app(datalocation=tmp_path / "missing.json").test_client()

    response = client.get("/data")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Graph data file not found"}


def test_data_route_reports_invalid_json(tmp_path) -> None:
    """The data route reports malformed JSON as a server error."""
    data_file = tmp_path / "invalid.json"
    data_file.write_text("{", encoding="utf-8")
    client = create_app(datalocation=data_file).test_client()

    response = client.get("/data")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Graph data file is invalid"}


def test_wheel_contains_compiled_frontend_assets() -> None:
    """The built Python wheel contains the frontend files used by Flask."""
    wheel_files = list(Path("dist").glob("*.whl"))
    if not wheel_files:
        pytest.skip("Run `uv build` before testing wheel contents.")

    with zipfile.ZipFile(wheel_files[0]) as wheel:
        assert frontend_asset_paths() <= set(wheel.namelist())


def test_source_distribution_contains_compiled_frontend_assets() -> None:
    """The source archive contains the compiled frontend files used by Flask."""
    source_archives = list(Path("dist").glob("*.tar.gz"))
    if not source_archives:
        pytest.skip("Run `uv build` before testing source distribution contents.")

    with tarfile.open(source_archives[0], "r:gz") as source_archive:
        archive_paths = {member.name for member in source_archive.getmembers()}
        assert all(
            any(member_path.endswith(asset_path) for member_path in archive_paths)
            for asset_path in frontend_asset_paths()
        )
