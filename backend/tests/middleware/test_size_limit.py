from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request_size_limiting(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_REQUEST_SIZE_BYTES", 10)
    
    # Send a request larger than 10 bytes
    payload = {"data": "This is a very long string that exceeds 10 bytes"}
    
    # POST to an endpoint (we'll just use the health check and mock a POST or use a real POST endpoint if exists)
    # The middleware checks Content-Length header, which is set automatically by TestClient based on json size
    response = client.post("/api/v1/health/live", json=payload)
    
    assert response.status_code == 413
    assert response.json()["error"]["error_code"] == "PAYLOAD_TOO_LARGE"
    
def test_request_size_limiting_allowed(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_REQUEST_SIZE_BYTES", 1000)
    
    payload = {"data": "small"}
    response = client.post("/api/v1/health/live", json=payload)
    # the endpoint doesn't support POST, so we expect 405 Method Not Allowed, but NOT 413!
    assert response.status_code == 405
