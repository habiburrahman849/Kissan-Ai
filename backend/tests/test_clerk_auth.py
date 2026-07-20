import sys
from pathlib import Path

# Add backend directory to python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal, init_db
from app.db.models import Farmer

client = TestClient(app)


def test_auth_config():
    response = client.get("/api/auth/config")
    assert response.status_code == 200
    data = response.json()
    assert "publishableKey" in data
    assert "clerk_enabled" in data
    assert "google_enabled" in data
    assert "guest_enabled" in data


def test_verify_endpoint():
    init_db()
    db: Session = SessionLocal()
    try:
        payload = {
            "clerk_id": "test_clerk_user_777",
            "email": "verify.test@kissan.ai",
            "name": "Verify Test Farmer",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        response = client.post("/api/auth/verify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["farmer"]["email"] == "verify.test@kissan.ai"

        farmer = db.query(Farmer).filter(Farmer.clerk_id == "test_clerk_user_777").first()
        assert farmer is not None
        db.delete(farmer)
        db.commit()
        print("SUCCESS: /api/auth/verify test passed!")
    finally:
        db.close()


def test_guest_endpoint():
    init_db()
    db: Session = SessionLocal()
    try:
        response = client.post("/api/auth/guest", json={"name": "Guest Farmer"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["farmer"]["is_guest"] is True

        farmer = db.query(Farmer).filter(Farmer.id == data["user_id"]).first()
        assert farmer is not None
        db.delete(farmer)
        db.commit()
        print("SUCCESS: /api/auth/guest test passed!")
    finally:
        db.close()


if __name__ == "__main__":
    test_auth_config()
    test_verify_endpoint()
    test_guest_endpoint()
    print("ALL AUTH ENDPOINT TESTS PASSED!")
