from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_find_events(client):
    response = client.get("/api/v1/events/")
    assert response.status_code == 200
    res_json = response.json()

    assert res_json["success"] is True
    assert res_json["message"] is not None

    data = res_json["data"]
    assert len(data) == 2

    first_event = data[0]
    expected_keys = {"id", "title", "dates", "place", "artists", "event_start_date"}
    assert expected_keys.issubset(first_event.keys())

    assert isinstance(first_event["artists"], list)
    assert len(first_event["artists"]) > 0
    assert "name" in first_event["artists"][0]
