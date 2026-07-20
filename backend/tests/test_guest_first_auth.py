import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_guest_first_auth_flow():
    # 1. Test GET /api/auth/config
    res = client.get("/api/auth/config")
    assert res.status_code == 200
    assert res.json()["guest_enabled"] is True

    # 2. Test POST /api/auth/guest
    res = client.post("/api/auth/guest", json={"name": "Guest Test Farmer"})
    assert res.status_code == 200
    guest_data = res.json()
    assert "access_token" in guest_data
    assert guest_data["farmer"]["is_guest"] is True
    guest_token = guest_data["access_token"]
    guest_id = guest_data["user_id"]

    # 3. Test POST /api/auth/convert-guest
    email = f"test_farmer_{guest_id}@kissan.ai"
    convert_res = client.post(
        "/api/auth/convert-guest",
        headers={"Authorization": f"Bearer {guest_token}"},
        json={"email": email, "password": "password123", "name": "Real Farmer"}
    )
    assert convert_res.status_code == 200
    converted_data = convert_res.json()
    assert converted_data["farmer"]["is_guest"] is False
    assert converted_data["farmer"]["email"] == email
    assert converted_data["farmer"]["name"] == "Real Farmer"

    # 4. Test POST /api/auth/login
    login_res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"}
    )
    assert login_res.status_code == 200
    assert login_res.json()["user_id"] == guest_id

    print("ALL GUEST-FIRST AUTH TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_guest_first_auth_flow()
