"""
Interactive CLI for testing the LLM Task Extraction Service.
Run with: .venv/Scripts/python test_llm_interactive.py
"""

import asyncio
import os
from datetime import date
from dotenv import load_dotenv

from app.services.llm_service import GeminiLLMService, MockLLMService, InvalidTaskInputError, LLMServiceError

load_dotenv()


async def main():
    api_key = os.getenv("GEMINI_API_KEY", "")
    has_gemini_key = bool(api_key and api_key != "your_gemini_api_key_here")

    print("\n" + "=" * 60)
    print("🤖 AI Task Assistant — LLM Service Test Harness")
    print("=" * 60)
    
    if has_gemini_key:
        print("1. Use Live Google Gemini (gemini-2.5-flash)")
        print("2. Use Mock LLM Service (Offline)")
        choice = input("\nSelect provider [1/2] (default: 1): ").strip()
        use_gemini = choice != "2"
    else:
        print("ℹ️  GEMINI_API_KEY not set in .env -> Using Mock LLM Service.")
        use_gemini = False

    service = GeminiLLMService() if use_gemini else MockLLMService(reference_date=date.today())
    provider_name = "Gemini LLM" if use_gemini else "Mock LLM"
    print(f"\n[Active Provider: {provider_name}]")
    print("Type any task description (or 'quit' / 'exit' to stop):\n")

    while True:
        try:
            user_input = input("Enter task text > ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not user_input:
                continue

            result = await service.parse_task_from_text(user_input)
            print("\n  Extracted Task Result:")
            print(f"   ├─ Title:       {result.title}")
            print(f"   ├─ Description: {result.description}")
            print(f"   ├─ Priority:    {result.priority.value.upper()}")
            print(f"   └─ Due Date:    {result.due_date}")
            print("-" * 50)

        except InvalidTaskInputError as e:
            print(f"\n  ❌ Invalid Task Error (HTTP 400): {e.message}\n")
        except LLMServiceError as e:
            print(f"\n  ⚠️  LLM Service Error (HTTP 502): {e.message}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    asyncio.run(main())
