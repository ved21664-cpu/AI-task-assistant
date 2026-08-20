"""
tests/test_llm.py
Unit tests for the LLM service implementations.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.schemas import PriorityEnum
from app.services.llm_service import (
    ExtractedTaskData,
    GeminiLLMService,
    InvalidTaskInputError,
    LLMServiceError,
    MockLLMService,
)


@pytest.fixture
def gemini_service():
    """Fixture for GeminiLLMService with a dummy API key."""
    return GeminiLLMService(api_key="test-key", model="test-model")


# ---------------------------------------------------------------------------
# GeminiLLMService Tests (Using Mocks)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_llm_tool_call_extraction(gemini_service):
    """Test that a valid tool call is correctly parsed into ExtractedTaskData."""
    # Mock the Google GenAI client response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_call = MagicMock()
    
    mock_call.name = "create_task"
    mock_call.args = {
        "title": "Buy groceries",
        "description": "Milk, eggs, and bread",
        "priority": "high",
        "due_date": "2026-08-25"
    }
    mock_response.function_calls = [mock_call]
    mock_client.models.generate_content.return_value = mock_response

    # Patch the _get_client method to return our mock
    with patch.object(gemini_service, "_get_client", return_value=mock_client):
        result = await gemini_service.parse_task_from_text("Buy groceries by Aug 25")
        
        assert isinstance(result, ExtractedTaskData)
        assert result.title == "Buy groceries"
        assert result.description == "Milk, eggs, and bread"
        assert result.priority == PriorityEnum.HIGH
        assert result.due_date == date(2026, 8, 25)


@pytest.mark.asyncio
async def test_llm_missing_due_date(gemini_service):
    """Test that missing or null due_date is parsed as None."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_call = MagicMock()
    
    mock_call.name = "create_task"
    mock_call.args = {
        "title": "Clean room",
        "description": "Vacuum and dust",
        "priority": "low"
        # due_date is missing
    }
    mock_response.function_calls = [mock_call]
    mock_client.models.generate_content.return_value = mock_response

    with patch.object(gemini_service, "_get_client", return_value=mock_client):
        result = await gemini_service.parse_task_from_text("Clean my room whenever")
        assert result.title == "Clean room"
        assert result.due_date is None


@pytest.mark.asyncio
async def test_llm_priority_inference(gemini_service):
    """Test that all three priority values map correctly, and fallback to medium."""
    priorities = [
        ("high", PriorityEnum.HIGH),
        ("medium", PriorityEnum.MEDIUM),
        ("low", PriorityEnum.LOW),
        ("invalid_stuff", PriorityEnum.MEDIUM),  # Fallback
        ("", PriorityEnum.MEDIUM)  # Fallback
    ]
    
    for input_prio, expected_enum in priorities:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_call = MagicMock()
        
        mock_call.name = "create_task"
        mock_call.args = {
            "title": "Task",
            "priority": input_prio
        }
        mock_response.function_calls = [mock_call]
        mock_client.models.generate_content.return_value = mock_response

        with patch.object(gemini_service, "_get_client", return_value=mock_client):
            result = await gemini_service.parse_task_from_text("Task")
            assert result.priority == expected_enum


def test_llm_relative_date_resolution(gemini_service):
    """Test _parse_extracted_args parses valid dates and ignores invalid ones."""
    # Valid date
    res1 = gemini_service._parse_extracted_args({"title": "A", "due_date": "2026-10-31"})
    assert res1.due_date == date(2026, 10, 31)
    
    # Invalid date format
    res2 = gemini_service._parse_extracted_args({"title": "A", "due_date": "next friday"})
    assert res2.due_date is None
    
    # Empty date
    res3 = gemini_service._parse_extracted_args({"title": "A", "due_date": ""})
    assert res3.due_date is None


@pytest.mark.asyncio
async def test_llm_failure_maps_to_502(gemini_service):
    """Test that an unhandled SDK exception is wrapped in LLMServiceError."""
    mock_client = MagicMock()
    # Make the API call raise an exception
    mock_client.models.generate_content.side_effect = Exception("API rate limit exceeded")

    with patch.object(gemini_service, "_get_client", return_value=mock_client):
        with pytest.raises(LLMServiceError) as exc_info:
            await gemini_service.parse_task_from_text("Do something")
        
        assert "LLM processing failed" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_llm_reject_task(gemini_service):
    """Test that reject_task tool call raises InvalidTaskInputError."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_call = MagicMock()
    
    mock_call.name = "reject_task"
    mock_call.args = {"reason": "Not a valid task"}
    mock_response.function_calls = [mock_call]
    mock_client.models.generate_content.return_value = mock_response

    with patch.object(gemini_service, "_get_client", return_value=mock_client):
        with pytest.raises(InvalidTaskInputError) as exc_info:
            await gemini_service.parse_task_from_text("Hello world")
        
        assert "Not a valid task" in str(exc_info.value)


# ---------------------------------------------------------------------------
# MockLLMService Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mock_llm_service():
    """Test MockLLMService behavior and edge cases."""
    # Set a fixed reference date for predictability
    mock_service = MockLLMService(reference_date=date(2026, 8, 21))
    
    # Test valid task extraction
    res1 = await mock_service.parse_task_from_text("Buy milk by friday high priority")
    assert "Buy milk" in res1.title
    assert res1.priority == PriorityEnum.HIGH
    assert res1.due_date == date(2026, 8, 21)
    
    # Test relative date 'tomorrow'
    res2 = await mock_service.parse_task_from_text("Call mom tomorrow low priority")
    assert res2.priority == PriorityEnum.LOW
    assert res2.due_date == date(2026, 8, 22)
    
    # Test simulated failure
    with pytest.raises(LLMServiceError):
        await mock_service.parse_task_from_text("simulate_llm_failure")
        
    # Test invalid input rejection
    with pytest.raises(InvalidTaskInputError):
        await mock_service.parse_task_from_text("hello")
