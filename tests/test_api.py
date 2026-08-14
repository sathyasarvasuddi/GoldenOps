from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_orders():
    response = client.get("/api/orders")

    assert response.status_code == 200


def test_payment_error():
    response = client.post(
        "/api/payments?simulate=error"
    )

    assert response.status_code == 500
