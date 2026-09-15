from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "local"


def test_health_response_has_request_id_header():
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
