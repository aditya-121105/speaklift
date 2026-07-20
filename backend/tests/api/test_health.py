from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_probe():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "diagnostics" in data
    assert "app_name" in data["diagnostics"]
    assert "version" in data["diagnostics"]
    assert "uptime_seconds" in data["diagnostics"]

def test_readiness_probe_success():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "llm_provider" in data
    assert "diagnostics" in data

def test_request_id_in_headers():
    response = client.get("/api/v1/health/live")
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
