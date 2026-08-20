# AI-Powered Task Assistant

An intelligent, API-driven task management system built with **FastAPI** that allows users to create tasks using natural language. The application uses **Google Gemini 2.5 Flash** (via Tool Calling) to automatically extract structured data (titles, descriptions, priorities, and deadlines) from conversational input.

## 🚀 Features

- **Natural Language Task Creation:** Send conversational input like *"Remind me to buy milk by next Friday, high priority"* and let the AI extract the exact date, priority, and task details.
- **Strict Validation:** Built on Pydantic V2 to enforce data schemas.
- **RESTful API:** Standard `GET`, `POST`, `PUT`, and `DELETE` endpoints for full CRUD operations.
- **Robust Error Handling:** Safely handles LLM hallucinations, network timeouts, and gibberish inputs with standardized HTTP status codes (400, 422, 502).
- **Clean Architecture:** Strict separation between routing, business logic (LLM services), and data persistence layers.
- **High Testability:** Fully mocked integration tests allowing for CI/CD pipelines without hitting LLM rate limits.

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Validation:** Pydantic V2
- **AI Integration:** Google GenAI SDK
- **Testing:** Pytest & HTTPX
- **Server:** Uvicorn

## ⚙️ Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ved21664-cpu/AI-task-assistant.git
   cd AI-task-assistant
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```ini
   GEMINI_API_KEY=your_real_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

5. **Run the server:**
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

6. **View Interactive API Documentation:**
   Open your browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to test the API directly!

## 🧪 Testing

The repository contains both integration tests and unit tests.

To run the entire test suite:
```powershell
pytest -v tests/
```

- `tests/test_tasks.py`: Fast integration tests mocking the LLM service to guarantee routing and database logic.
- `tests/test_llm.py`: Unit tests ensuring that LLM tool-calling extraction and fallback logic works flawlessly.

## 📚 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task from a natural language `"input"` string. |
| `GET` | `/tasks` | Retrieve a list of all saved tasks. |
| `GET` | `/tasks/{task_id}` | Retrieve a specific task by its ID. |
| `PUT` | `/tasks/{task_id}` | Update an existing task manually. |
| `DELETE`| `/tasks/{task_id}` | Delete a task. |

## 🏗️ Architecture

For a deep dive into the system's Domain-Driven Design, Dependency Injection setup, and data flow sequences, refer to the [architecture document](docs/architecture.md).
