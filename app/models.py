"""
app/models.py
Internal domain model for a Task.
Decoupled from Pydantic HTTP request/response schemas.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class TaskModel:
    """Internal representation of a task stored in the in-memory repository."""

    id: int
    title: str
    description: str
    priority: str           # Values: "low" | "medium" | "high"
    due_date: Optional[date] = None
