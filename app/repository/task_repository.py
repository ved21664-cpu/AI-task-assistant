"""
app/repository/task_repository.py
In-memory data store and CRUD operations for TaskModel instances.
"""

from datetime import date
from typing import Dict, List, Optional
from app.models import TaskModel
from app.schemas import PriorityEnum, UpdateTaskRequest


class TaskRepository:
    """In-memory CRUD repository for tasks with auto-incrementing ID."""

    def __init__(self) -> None:
        self._tasks: Dict[int, TaskModel] = {}
        self._counter: int = 1

    def create(
        self,
        title: str,
        description: str,
        priority: PriorityEnum,
        due_date: Optional[date] = None,
    ) -> TaskModel:
        """Create a new task with an auto-incremented ID and store it in memory."""
        priority_val = (
            priority.value if isinstance(priority, PriorityEnum) else str(priority)
        )
        task = TaskModel(
            id=self._counter,
            title=title,
            description=description,
            priority=priority_val,
            due_date=due_date,
        )
        self._tasks[self._counter] = task
        self._counter += 1
        return task

    def get_all(self) -> List[TaskModel]:
        """Retrieve all stored tasks as a list."""
        return list(self._tasks.values())

    def get_by_id(self, task_id: int) -> Optional[TaskModel]:
        """Retrieve a task by its unique identifier, or return None if not found."""
        return self._tasks.get(task_id)

    def update(
        self,
        task_id: int,
        update_data: UpdateTaskRequest,
    ) -> Optional[TaskModel]:
        """Update an existing task's fields, returning the updated model or None if not found."""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        priority_val = (
            update_data.priority.value
            if isinstance(update_data.priority, PriorityEnum)
            else str(update_data.priority)
        )
        task.title = update_data.title
        task.description = update_data.description
        task.priority = priority_val
        task.due_date = update_data.due_date
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Return True if deleted, or False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all stored tasks and reset counter. Used for test isolation."""
        self._tasks.clear()
        self._counter = 1
