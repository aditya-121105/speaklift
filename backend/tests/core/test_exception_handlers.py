from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.exception_handlers import register_exception_handlers
from app.shared.exceptions import SpeakLiftException

app = FastAPI()
register_exception_handlers(app)

class DummyDomainException(SpeakLiftException):
    status_code = 400
    def __init__(self):
        super().__init__(detail="Dummy domain error")

@app.get("/domain-error")
def trigger_domain_error():
    raise DummyDomainException()

@app.get("/generic-error")
def trigger_generic_error():
    raise ValueError("Something bad happened internally")

client = TestClient(app, raise_server_exceptions=False)

def test_domain_exception_handler():
    response = client.get("/domain-error")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    error = data["error"]
    assert error["error_code"] == "DummyDomainException"
    assert error["message"] == "Dummy domain error"
    assert error["status"] == 400
    assert "timestamp" in error
    assert "request_id" in error

def test_generic_exception_handler():
    response = client.get("/generic-error")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    error = data["error"]
    assert error["error_code"] == "INTERNAL_SERVER_ERROR"
    assert error["message"] == "An unexpected error occurred."
    assert error["status"] == 500
    assert "timestamp" in error
    assert "request_id" in error
