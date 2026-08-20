"""
app/services/llm_service.py
LLM provider abstraction, Gemini tool calling implementation, and Mock provider.
"""

import os
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from app.schemas import ExtractedTaskData, PriorityEnum

# Load environment variables
load_dotenv()


class LLMServiceError(Exception):
    """Raised when the LLM provider fails, times out, or returns invalid structure."""

    def __init__(self, message: str = "Unable to process task using the LLM service") -> None:
        super().__init__(message)
        self.message = message


class InvalidTaskInputError(Exception):
    """Raised when the natural language input does not contain a valid actionable task."""

    def __init__(self, message: str = "Invalid task input") -> None:
        super().__init__(message)
        self.message = message


class BaseLLMService(ABC):
    """Abstract interface for natural-language task extraction services."""

    @abstractmethod
    async def parse_task_from_text(self, text: str) -> ExtractedTaskData:
        """Parse natural-language task input into structured ExtractedTaskData."""
        raise NotImplementedError


# JSON schema definition for the create_task function tool
CREATE_TASK_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "title": {
            "type": "STRING",
            "description": "Short, clear title summarizing the task (e.g. 'Submit project report')",
        },
        "description": {
            "type": "STRING",
            "description": "Full description explaining what needs to be done",
        },
        "priority": {
            "type": "STRING",
            "enum": ["low", "medium", "high"],
            "description": "Priority level of the task. Default to 'medium' if unspecified.",
        },
        "due_date": {
            "type": "STRING",
            "description": (
                "Due date in YYYY-MM-DD format calculated relative to the reference date provided. "
                "Set to empty string or null if no deadline or due date is mentioned."
            ),
        },
    },
    "required": ["title", "description", "priority"],
}

REJECT_TASK_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "reason": {
            "type": "STRING",
            "description": "Reason why the input cannot be converted into an actionable task",
        }
    },
    "required": ["reason"],
}


class GeminiLLMService(BaseLLMService):
    """Google Gemini implementation of BaseLLMService using tool calling."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None

    def _get_client(self):
        """Lazy-initialize Google GenAI client."""
        if self._client is None:
            if not self.api_key or self.api_key == "your_gemini_api_key_here":
                raise LLMServiceError("GEMINI_API_KEY is not configured or is invalid")
            try:
               
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                raise LLMServiceError(f"Failed to initialize Gemini client: {exc}") from exc
        return self._client

    async def parse_task_from_text(self, text: str) -> ExtractedTaskData:
        """Invokes Gemini with function calling to extract structured task data."""
        clean_text = text.strip()
        if not clean_text:
            raise InvalidTaskInputError("Task input cannot be empty")

        try:
            client = self._get_client()
            from google.genai import types

            now = datetime.now()
            current_date_str = now.strftime("%A, %Y-%m-%d")

            system_instruction = (
                f"You are an AI Task Assistant. Today's reference date is {current_date_str}.\n"
                "Your job is to analyze user input and extract structured task information.\n"
                "If the user input describes an actionable task, call the `create_task` tool.\n"
                "- Extract a concise title and a detailed description.\n"
                "- Infer priority as 'low', 'medium', or 'high'. Default to 'medium' if not specified.\n"
                "- If a deadline is mentioned (e.g. 'tomorrow', 'by Friday', 'next week'), resolve it to an exact YYYY-MM-DD date based on today's date.\n"
                "- If no deadline is mentioned, set due_date to null.\n"
                "If the user input is NOT an actionable task (such as a greeting like 'hello', random gibberish, a question, or general conversation), "
                "call the `reject_task` tool."
            )

            tool = types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="create_task",
                        description="Create a structured task object from natural language.",
                        parameters=CREATE_TASK_TOOL_SCHEMA,
                    ),
                    types.FunctionDeclaration(
                        name="reject_task",
                        description="Reject input that is not an actionable task.",
                        parameters=REJECT_TASK_TOOL_SCHEMA,
                    ),
                ]
            )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[tool],
                temperature=0.1,
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=clean_text,
                config=config,
            )

            # Check for tool/function calls in response
            function_calls = getattr(response, "function_calls", None)
            if not function_calls and hasattr(response, "candidates") and response.candidates:
                first_cand = response.candidates[0]
                if hasattr(first_cand, "content") and first_cand.content and first_cand.content.parts:
                    for part in first_cand.content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            function_calls = [part.function_call]
                            break

            if not function_calls:
                # If model responded with plain text and refused or could not extract
                raise InvalidTaskInputError("Input could not be recognized as a valid task")

            first_call = function_calls[0]
            call_name = getattr(first_call, "name", "")
            args = getattr(first_call, "args", {}) or {}

            if call_name == "reject_task":
                raise InvalidTaskInputError(args.get("reason", "Invalid task input"))

            if call_name == "create_task":
                return self._parse_extracted_args(args)

            raise InvalidTaskInputError("Unrecognized action extracted from input")

        except (InvalidTaskInputError, LLMServiceError):
            raise
        except Exception as exc:
            raise LLMServiceError(f"LLM processing failed: {exc}") from exc

    def _parse_extracted_args(self, args: Dict[str, Any]) -> ExtractedTaskData:
        """Validates and parses raw dictionary arguments into ExtractedTaskData."""
        title = str(args.get("title", "")).strip()
        description = str(args.get("description", "")).strip()
        if not title:
            raise InvalidTaskInputError("Extracted task title is missing")

        raw_priority = str(args.get("priority", "medium")).lower().strip()
        if raw_priority not in ("low", "medium", "high"):
            raw_priority = "medium"
        priority = PriorityEnum(raw_priority)

        due_date: Optional[date] = None
        raw_due_date = args.get("due_date")
        if raw_due_date and str(raw_due_date).strip() and str(raw_due_date).lower() not in ("null", "none"):
            try:
                due_date = date.fromisoformat(str(raw_due_date).strip()[:10])
            except ValueError:
                due_date = None

        return ExtractedTaskData(
            title=title,
            description=description or title,
            priority=priority,
            due_date=due_date,
        )


class MockLLMService(BaseLLMService):
    """Deterministic mock implementation of BaseLLMService for testing and offline development."""

    def __init__(self, reference_date: Optional[date] = None) -> None:
        self.reference_date = reference_date or date(2026, 8, 21)  # Friday

    async def parse_task_from_text(self, text: str) -> ExtractedTaskData:
        clean_text = text.strip()

        # Simulated failure test case
        if clean_text == "simulate_llm_failure":
            raise LLMServiceError("Simulated LLM service failure")

        # Invalid/gibberish detection
        lower = clean_text.lower()
        if (
            lower
            in (
                "hello",
                "hi",
                "hey",
                "what is the weather",
                "tell me a joke",
                "asdf123",
                "12345",
                "random gibberish",
                "xyz???",
            )
            or any(
                p in lower
                for p in ["weather", "hello world", "tell me a joke", "how are you", "random gibberish", "asdf"]
            )
            or len(clean_text) < 4
        ):
            raise InvalidTaskInputError("Input is not an actionable task")

        # Priority extraction
        priority = PriorityEnum.MEDIUM
        if re.search(r"\b(high priority|urgent|critical|asap|important)\b", lower):
            priority = PriorityEnum.HIGH
        elif re.search(r"\b(low priority|minor|whenever|someday|no rush)\b", lower):
            priority = PriorityEnum.LOW

        # Date extraction relative to reference_date (Default 2026-08-21 Friday)
        due_date: Optional[date] = None
        if "tomorrow" in lower:
            due_date = self.reference_date + timedelta(days=1)
        elif "by friday" in lower or "friday" in lower:
            due_date = self.reference_date  # 2026-08-21 is Friday
        elif "next monday" in lower:
            due_date = self.reference_date + timedelta(days=3)
        elif "in 3 days" in lower:
            due_date = self.reference_date + timedelta(days=3)
        elif "next week" in lower:
            due_date = self.reference_date + timedelta(days=7)

        # Title and description extraction
        title = clean_text
        for phrase in [
            " and make it high priority",
            " and make it low priority",
            " high priority",
            " low priority",
            " by friday",
            " tomorrow",
            " next monday",
        ]:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            title = pattern.sub("", title)
        title = title.strip().rstrip(".").capitalize()

        description = clean_text.strip()

        return ExtractedTaskData(
            title=title or "Task",
            description=description,
            priority=priority,
            due_date=due_date,
        )
