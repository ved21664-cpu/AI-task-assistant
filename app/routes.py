"""
app/routes.py
FastAPI route handlers for the Task Management API.
All routes operate through BaseLLMService and TaskRepository
with zero LLM vendor SDK imports in this file.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.dependencies import get_llm_service, get_task_repository
from app.repository.task_repository import TaskRepository
from app.schemas import CreateTaskRequest, Task, UpdateTaskRequest
from app.services.llm_service import BaseLLMService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _model_to_schema(task) -> Task:
    """Convert a TaskModel instance to the Task response schema."""
    return Task(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
    )


# ---------------------------------------------------------------------------
# POST /tasks  — Create Task from Natural Language
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    operation_id="createTask",
    summary="Create a task from natural-language input",
    description=(
        "Accepts a natural-language task description, uses the LLM to convert "
        "the input into a structured task, validates the result, and stores the task."
    ),
    responses={
        400: {"description": "Invalid request or invalid task data"},
        422: {"description": "Request validation error"},
        502: {"description": "LLM provider failure"},
    },
)
async def create_task(
    request: CreateTaskRequest,
    llm_service: BaseLLMService = Depends(get_llm_service),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> Task:
    extracted = await llm_service.parse_task_from_text(request.input)
    task = task_repo.create(
        title=extracted.title,
        description=extracted.description,
        priority=extracted.priority,
        due_date=extracted.due_date,
    )
    return _model_to_schema(task)


# ---------------------------------------------------------------------------
# GET /tasks  — Retrieve All Tasks
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[Task],
    status_code=status.HTTP_200_OK,
    operation_id="getTasks",
    summary="Retrieve all tasks",
    description="Returns all tasks currently stored by the application.",
)
async def get_tasks(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> List[Task]:
    return [_model_to_schema(t) for t in task_repo.get_all()]


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}  — Retrieve Specific Task
# ---------------------------------------------------------------------------

@router.get(
    "/{task_id}",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    operation_id="getTask",
    summary="Retrieve a task by ID",
    description="Returns a single task using its unique task ID.",
    responses={
        404: {"description": "Task not found"},
        422: {"description": "Invalid path parameter"},
    },
)
async def get_task(
    task_id: int = Path(..., ge=1, description="Unique identifier of the task"),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> Task:
    task = task_repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return _model_to_schema(task)


# ---------------------------------------------------------------------------
# PUT /tasks/{task_id}  — Update Task
# ---------------------------------------------------------------------------

@router.put(
    "/{task_id}",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    operation_id="updateTask",
    summary="Update a task",
    description="Updates an existing task using structured task data.",
    responses={
        404: {"description": "Task not found"},
        422: {"description": "Request or path parameter validation error"},
    },
)
async def update_task(
    update_data: UpdateTaskRequest,
    task_id: int = Path(..., ge=1, description="Unique identifier of the task"),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> Task:
    task = task_repo.update(task_id, update_data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return _model_to_schema(task)


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id}  — Delete Task
# ---------------------------------------------------------------------------

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteTask",
    summary="Delete a task",
    description="Deletes an existing task using its unique task ID.",
    responses={
        404: {"description": "Task not found"},
        422: {"description": "Invalid path parameter"},
    },
)
async def delete_task(
    task_id: int = Path(..., ge=1, description="Unique identifier of the task"),
    task_repo: TaskRepository = Depends(get_task_repository),
) -> None:
    deleted = task_repo.delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
