"""
app/dependencies.py
Dependency provider functions for FastAPI dependency injection.
"""

import os

from app.repository.task_repository import TaskRepository
from app.services.llm_service import BaseLLMService, GeminiLLMService, MockLLMService

# Application-wide singleton in-memory repository instance
_task_repository = TaskRepository()


def get_task_repository() -> TaskRepository:
    """Dependency provider for TaskRepository."""
    return _task_repository


def get_llm_service() -> BaseLLMService:
    """Dependency provider for BaseLLMService.

    Uses GeminiLLMService when GEMINI_API_KEY is set in the environment,
    otherwise falls back to MockLLMService for offline/testing usage.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        return GeminiLLMService(api_key=api_key)
    return MockLLMService()
