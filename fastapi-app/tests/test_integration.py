import requests

BASE_URL = "http://163.239.77.79:8002"


def test_deployed_get_todos():
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deployed_create_todo():
    todo = {
        "id": 999,
        "title": "Integration Test",
        "description": "통합 테스트용 항목",
        "completed": False,
        "due_date": None,
        "priority": "중"
    }
    response = requests.post(f"{BASE_URL}/todos", json=todo)
    assert response.status_code == 200


def test_deployed_delete_todo():
    response = requests.delete(f"{BASE_URL}/todos/999")
    assert response.status_code == 200
