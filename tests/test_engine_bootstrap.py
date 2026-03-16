import pytest
from fastapi.testclient import TestClient

from control.file_guard import FileGuard
from engine.server import create_app


def test_health_endpoint():
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "ok"
    assert "engine" in body["features"]


def test_file_guard_blocks_protected_directory(tmp_path):
    guard = FileGuard(protected=[tmp_path])
    protected_file = tmp_path / "secret.txt"
    protected_file.write_text("data")
    assert guard.is_allowed(str(protected_file)) is False
    with pytest.raises(PermissionError):
        guard.ensure_allowed(str(protected_file))
