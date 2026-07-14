from fastapi.testclient import TestClient

from app.api.main import app
from app.core.database import SessionLocal
from app.core.models import User

client = TestClient(app)


def test_root_ok():
    assert client.get("/").status_code == 200


def test_events_returns_data():
    r = client.get("/events", params={"lat": 28.36, "lon": 79.43, "days": 3})
    assert r.status_code == 200
    assert "events" in r.json()


def test_events_rejects_bad_latitude():
    assert client.get("/events", params={"lat": 999, "lon": 0}).status_code == 422


def test_subscribe_creates_then_updates():
    r1 = client.post("/subscribe", json={"email": "t@example.com", "lat": 10, "lon": 20})
    assert r1.json()["status"] == "created"
    r2 = client.post("/subscribe", json={"email": "t@example.com", "lat": 30, "lon": 40})
    assert r2.json()["status"] == "updated"
    with SessionLocal() as s:
        assert s.query(User).filter(User.email == "t@example.com").count() == 1


def test_subscribe_rejects_bad_email():
    assert client.post("/subscribe", json={"email": "nope", "lat": 1, "lon": 2}).status_code == 422
