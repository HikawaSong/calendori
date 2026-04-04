from fastapi.testclient import TestClient
from app.main import app
from app.models import Event, User

client = TestClient(app)


def test_create_project_for_event(client, db_session):
    event = db_session.query(Event).first()

    assert event is not None, "数据库中没有预置的 Event 数据，请检查 create_test_data()"
    event_id = event.id
    # 2. 为该 Event 创建 Project
    project_data = {
        "name": "Project A",
        "project_type": "花篮",
        "description": "First Project",
        "event_id": event_id,
    }
    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 201, f"创建失败: {response.text}"

    print("\n[DEBUG] Status Code:", response.status_code)
    print("[DEBUG] Response JSON:", response.json())

    assert response.status_code == 201
    assert response.json()["name"] == "Project A"
    assert response.json()["event_id"] == event_id
