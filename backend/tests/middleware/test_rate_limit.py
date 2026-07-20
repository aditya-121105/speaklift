from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rate_limiting(monkeypatch):
    from app.core.config import settings
    from app.middleware.rate_limit import _rate_limits
    _rate_limits.clear()
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_MINUTE", 2)
    
    # First request
    response1 = client.get("/api/v1/health/live")
    assert response1.status_code == 200
    
    # Second request
    response2 = client.get("/api/v1/health/live")
    assert response2.status_code == 200
    
    # Third request - should be blocked
    response3 = client.get("/api/v1/health/live")
    assert response3.status_code == 429
    assert "Retry-After" in response3.headers
    assert response3.json()["error"]["error_code"] == "RATE_LIMIT_EXCEEDED"
