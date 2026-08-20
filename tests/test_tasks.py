"""
tests/test_tasks.py
Integration tests for the Task Management API routes.
Uses FastAPI TestClient and MockLLMService dependency override.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.dependencies import _task_repository, get_llm_service
from app.main import app
from app.services.llm_service import MockLLMService


@pytest.fixture(autouse=True)
def clean_repository_and_override_llm():
    """Clear repository before and after each test and override LLM service with MockLLMService."""
    _task_repository.clear()
    app.dependency_overrides[get_llm_service] = lambda: MockLLMService()
    yield
    _task_repository.clear()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Test client instance."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# POST /tasks Tests
# ---------------------------------------------------------------------------

def test_create_task_success(client: TestClient):
    """Test creating a valid task returns 201 and structured task."""
    response = client.post(
        "/tasks",
        json={"input": "Prepare quarterly review presentation by next Friday, high priority"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 1
    assert "Prepare quarterly review presentation" in data["title"]
    assert data["priority"] == "high"
    assert data["due_date"] is not None


def test_create_task_empty_input(client: TestClient):
    """Test empty string input returns 422 validation error."""
    response = client.post("/tasks", json={"input": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


def test_create_task_missing_input_field(client: TestClient):
    """Test missing input field returns 422 validation error."""
    response = client.post("/tasks", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


def test_create_task_irrelevant_input(client: TestClient):
    """Test nonsensical/non-actionable input raises 400 Bad Request."""
    response = client.post("/tasks", json={"input": "hello world what is the weather today"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Input is not an actionable task" in data["detail"]


# ---------------------------------------------------------------------------
# GET /tasks Tests
# ---------------------------------------------------------------------------

def test_get_all_tasks_empty(client: TestClient):
    """Test getting all tasks when repository is empty returns 200 with []."""
    response = client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_all_tasks_populated(client: TestClient):
    """Test getting all tasks when tasks exist returns full list with 200."""
    _task_repository.create(title="Task 1", description="Desc 1", priority="low", due_date=None)
    _task_repository.create(title="Task 2", description="Desc 2", priority="medium", due_date="2026-09-01")

    response = client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


# ---------------------------------------------------------------------------
# GET /tasks/{task_id} Tests
# ---------------------------------------------------------------------------

def test_get_task_by_id_success(client: TestClient):
    """Test retrieving an existing task by ID returns 200 with task."""
    created = _task_repository.create(
        title="Test Task",
        description="Testing details",
        priority="high",
        due_date="2026-10-15",
    )
    response = client.get(f"/tasks/{created.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created.id
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"


def test_get_task_by_id_not_found(client: TestClient):
    """Test retrieving non-existent task returns 404 with exact detail string."""
    response = client.get("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Task with id 999 not found"


def test_get_task_invalid_id(client: TestClient):
    """Test invalid task_id <= 0 returns 422 Unprocessable Entity."""
    response = client.get("/tasks/0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


# ---------------------------------------------------------------------------
# PUT /tasks/{task_id} Tests
# ---------------------------------------------------------------------------

def test_update_task_success(client: TestClient):
    """Test updating existing task returns 200 with updated task."""
    created = _task_repository.create(
        title="Original Title",
        description="Original Desc",
        priority="medium",
        due_date=None,
    )
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Desc",
        "priority": "high",
        "due_date": "2026-12-01",
    }
    response = client.put(f"/tasks/{created.id}", json=update_payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created.id
    assert data["title"] == "Updated Title"
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-12-01"


def test_update_task_not_found(client: TestClient):
    """Test updating non-existent task returns 404."""
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Desc",
        "priority": "low",
        "due_date": None,
    }
    response = client.put("/tasks/999", json=update_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Task with id 999 not found"


def test_update_task_invalid_priority(client: TestClient):
    """Test updating task with invalid priority returns 422."""
    created = _task_repository.create(
        title="Task",
        description="Desc",
        priority="low",
        due_date=None,
    )
    invalid_payload = {
        "title": "Task",
        "description": "Desc",
        "priority": "urgent",  # Invalid enum
        "due_date": None,
    }
    response = client.put(f"/tasks/{created.id}", json=invalid_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id} Tests
# ---------------------------------------------------------------------------

def test_delete_task_success(client: TestClient):
    """Test deleting existing task returns 204 No Content."""
    created = _task_repository.create(
        title="Task to delete",
        description="To be removed",
        priority="low",
        due_date=None,
    )
    response = client.delete(f"/tasks/{created.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert _task_repository.get_by_id(created.id) is None


def test_delete_task_not_found(client: TestClient):
    """Test deleting non-existent task returns 404."""
    response = client.delete("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Task with id 999 not found"
