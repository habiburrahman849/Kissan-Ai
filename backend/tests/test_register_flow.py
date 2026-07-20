import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_endpoint():
    # 1. Test weak password
    res = client.post("/api/auth/register", json={
        "email": "test_weak@kissan.ai",
        "password": "short",
        "full_name": "Test Short"
    })
    assert res.status_code == 400
    assert "8+ characters" in res.json()["detail"]

    # 2. Test successful signup
    email = f"user_signup_test_{Path(__file__).stat().st_mtime}@kissan.ai"
    res = client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Ali Farmer"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["farmer"]["email"] == email
    assert data["farmer"]["name"] == "Ali Farmer"
    assert data["farmer"]["is_guest"] is False

    # 3. Test duplicate email signup
    dup_res = client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Duplicate Ali"
    })
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.json()["detail"]

    print("ALL SIGNUP & REGISTER ENDPOINT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_register_endpoint()
