import pytest
import json
import os
import sys

# fastapi-app 루트를 sys.path에 추가해 main 모듈을 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
import main
from main import app, save_todos, TodoItem

client = TestClient(app)

TEST_TODO_FILE = os.path.join(os.path.dirname(__file__), "test_todo.json")


@pytest.fixture(autouse=True)
def cleanup(monkeypatch):
    """각 테스트 전후로 테스트 전용 임시 파일 사용 (실제 todo.json 보호)"""
    monkeypatch.setattr(main, "TODO_FILE", TEST_TODO_FILE)
    if os.path.exists(TEST_TODO_FILE):
        os.remove(TEST_TODO_FILE)
    yield
    if os.path.exists(TEST_TODO_FILE):
        os.remove(TEST_TODO_FILE)


# ── GET /todos ─────────────────────────────────────────────────────────────

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])

    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"


def test_get_todos_includes_new_fields():
    """due_date, priority 필드가 응답에 포함되는지 확인"""
    todo = TodoItem(
        id=1, title="Test", description="desc", completed=False,
        due_date="2025-12-31", priority="상"
    )
    save_todos([todo.model_dump()])

    data = client.get("/todos").json()[0]
    assert data["due_date"] == "2025-12-31"
    assert data["priority"] == "상"


# ── POST /todos ────────────────────────────────────────────────────────────

def test_create_todo():
    todo = {"id": 1, "title": "Test", "description": "Test description", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"


def test_create_todo_defaults():
    """due_date, priority 생략 시 기본값 확인"""
    todo = {"id": 2, "title": "Default Fields", "description": "desc", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["due_date"] is None
    assert response.json()["priority"] == "중"


def test_create_todo_with_due_date_and_priority():
    todo = {
        "id": 3, "title": "With Meta", "description": "desc", "completed": False,
        "due_date": "2025-06-30", "priority": "하"
    }
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["due_date"] == "2025-06-30"
    assert response.json()["priority"] == "하"


def test_create_todo_invalid():
    """필수 필드(description, completed) 누락 시 422"""
    todo = {"id": 1, "title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422


# ── PUT /todos/{id} ────────────────────────────────────────────────────────

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])

    updated = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_update_todo_new_fields():
    """due_date, priority 수정 확인"""
    todo = TodoItem(id=1, title="Test", description="desc", completed=False)
    save_todos([todo.model_dump()])

    updated = {
        "id": 1, "title": "Test", "description": "desc", "completed": False,
        "due_date": "2025-09-01", "priority": "상"
    }
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 200
    assert response.json()["due_date"] == "2025-09-01"
    assert response.json()["priority"] == "상"


def test_update_todo_not_found():
    updated = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 404


# ── DELETE /todos/{id} ─────────────────────────────────────────────────────

def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])

    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"


def test_delete_todo_not_found():
    """존재하지 않는 ID 삭제 — 현재 구현은 200 반환"""
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"


# ── GET / (HTML) ───────────────────────────────────────────────────────────

def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
