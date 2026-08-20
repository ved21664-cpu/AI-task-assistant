"""
app/schemas.py
Pydantic validation schemas and models for the AI-Powered Task Assistant API.
"""

from datetime import date
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class PriorityEnum(str, Enum):
    """Enumeration of allowed task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CreateTaskRequest(BaseModel):
    """Request schema for creating a task from natural language."""

    input: str = Field(
        ...,
        min_length=1,
        description="Natural-language description of the task",
        examples=["Submit my project report by Friday and make it high priority."],
    )


class UpdateTaskRequest(BaseModel):
    """Request schema for updating an existing task."""

    title: str = Field(
        ...,
        min_length=1,
        description="Task title",
        examples=["Submit final project report"],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Task description",
        examples=["Submit the completed project report"],
    )
    priority: PriorityEnum = Field(
        ...,
        description="Task priority",
        examples=[PriorityEnum.HIGH],
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date. May be null when no deadline exists.",
        examples=["2026-08-22"],
    )


class Task(BaseModel):
    """Response schema representing a task."""

    id: int = Field(
        ...,
        ge=1,
        description="Unique task identifier",
        examples=[1],
    )
    title: str = Field(
        ...,
        description="Task title",
        examples=["Submit project report"],
    )
    description: str = Field(
        ...,
        description="Task description",
        examples=["Submit the project report"],
    )
    priority: PriorityEnum = Field(
        ...,
        description="Task priority",
        examples=[PriorityEnum.HIGH],
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date",
        examples=["2026-08-21"],
    )

    model_config = ConfigDict(from_attributes=True)


class ExtractedTaskData(BaseModel):
    """Structured data extracted by the LLM via tool calling."""

    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        description="Task priority",
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Due date in YYYY-MM-DD format or null",
    )


class ErrorResponse(BaseModel):
    """Generic error response schema."""

    detail: str = Field(
        ...,
        description="Human-readable description of the error",
        examples=["Task with id 999 not found"],
    )


class ValidationError(BaseModel):
    """Schema representing an individual validation error detail."""

    loc: List[Union[str, int]] = Field(
        ...,
        description="Location of the validation error",
        examples=[["body", "priority"]],
    )
    msg: str = Field(
        ...,
        description="Validation error message",
        examples=["Input should be 'low', 'medium' or 'high'"],
    )
    type: str = Field(
        ...,
        description="Type of validation error",
        examples=["enum"],
    )


class ValidationErrorResponse(BaseModel):
    """Schema representing validation error response (HTTP 422)."""

    detail: List[ValidationError]
