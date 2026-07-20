import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "kissan-ai-memoryagent"}


def test_auth_and_chat_flow():
    # 1. Create guest
    res_guest = client.post("/api/auth/guest")
    assert res_guest.status_code == 200
    data_guest = res_guest.json()
    assert "access_token" in data_guest
    assert "user_id" in data_guest
    guest_token = data_guest["access_token"]
    guest_user_id = data_guest["user_id"]

    # 2. Register real user using guest data
    email = f"roundup_test_{guest_user_id}@kissan.ai"
    res_reg = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Test Roundup User",
            "guest_user_id": guest_user_id
        }
    )
    assert res_reg.status_code == 200
    data_reg = res_reg.json()
    user_token = data_reg["access_token"]
    real_user_id = data_reg["user_id"]

    # 3. Fetch profile
    res_me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == email
    assert me_data["full_name"] == "Test Roundup User"
    assert me_data["is_guest"] is False

    # 4. Send chat message
    res_chat = client.post(
        "/api/chat/message",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "message": "Assalam o alaikum, my wheat crop has yellow leaves in Multan",
            "session_id": "session_1"
        }
    )
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert "response" in chat_data
    assert chat_data["language"] == "ur"
    assert "CropAgent" in chat_data["agents_used"]

    # 5. Fetch weather
    res_weather = client.get("/api/weather?location=Multan")
    assert res_weather.status_code == 200
    w_data = res_weather.json()
    assert "temperature" in w_data
    assert "forecast" in w_data

    print("ALL FINAL ROUNDUP TEST CASES PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_health()
    test_auth_and_chat_flow()
