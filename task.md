# Task List — AI-Powered Task Assistant API

## Phase 1: Project Scaffolding & Configuration

- `[x]` **1.1** Create the full project directory structure as specified in the implementation plan:
  - `app/`, `app/repository/`, `app/services/`, `docs/`, `evaluation/`, `spec/`, `tests/`
- `[x]` **1.2** Verify `.env` file contains `GEMINI_API_KEY` and is excluded via `.gitignore`
- `[x]` **1.3** Verify `requirements.txt` lists all required dependencies:
  - `fastapi`, `uvicorn`, `pydantic`, `google-genai`, `pytest`, `httpx`, `python-dotenv`

---

## Phase 2: Domain Models (`app/models.py`)

- `[x]` **2.1** Create `app/models.py`
  - Define the `TaskModel` dataclass with fields: `id`, `title`, `description`, `priority`, `due_date`
  - Keep it decoupled from Pydantic HTTP schemas

---

## Phase 3: Pydantic Schemas (`app/schemas.py`)

- `[x]` **3.1** Create `app/schemas.py`
  - Define `PriorityEnum` with values `low`, `medium`, `high`
  - Define `CreateTaskRequest` with `input: str` (min_length=1)
  - Define `UpdateTaskRequest` with `title`, `description`, `priority`, `due_date` fields
  - Define `Task` response model with `id`, `title`, `description`, `priority`, `due_date`
  - Define `ExtractedTaskData` for structured LLM tool-call output
  - Define `ErrorResponse` with `detail: str`
  - Define `ValidationError` and `ValidationErrorResponse` for 422 responses

---

## Phase 4: Repository Layer (`app/repository/task_repository.py`)

- `[x]` **4.1** Create `app/repository/__init__.py` (empty)
- `[x]` **4.2** Create `app/repository/task_repository.py`
  - Implement in-memory `dict[int, TaskModel]` store with auto-incrementing integer counter
  - Implement `create(title, description, priority, due_date) -> TaskModel`
  - Implement `get_all() -> list[TaskModel]`
  - Implement `get_by_id(task_id) -> Optional[TaskModel]`
  - Implement `update(task_id, update_data) -> Optional[TaskModel]`
  - Implement `delete(task_id) -> bool`
  - Implement `clear() -> None` (for test isolation)

---

## Phase 5: LLM Service (`app/services/llm_service.py`)

- `[x]` **5.1** Create `app/services/__init__.py` (empty)
- `[x]` **5.2** Create `app/services/llm_service.py`
  - Define custom domain exceptions: `LLMServiceError` and `InvalidTaskInputError`
  - Define `BaseLLMService` abstract base class with:
    - `async def parse_task_from_text(self, text: str) -> ExtractedTaskData`
  - Define the `create_task` tool declaration JSON schema (with `title`, `description`, `priority`, `due_date` properties; `title`, `description`, `priority` required)
  - Implement `GeminiLLMService(BaseLLMService)`:
    - Load `GEMINI_API_KEY` from environment via `python-dotenv`
    - Inject current date into system prompt for temporal anchoring (e.g. `"Today is Friday, 2026-08-22"`)
    - Send prompt with tool declaration via Google GenAI SDK
    - Parse and validate tool call arguments into `ExtractedTaskData`
    - Detect irrelevant/non-task input and raise `InvalidTaskInputError`
    - Catch SDK/network errors and raise `LLMServiceError`
  - Implement `MockLLMService(BaseLLMService)` for deterministic offline testing

---

## Phase 6: FastAPI App Initialization (`app/main.py`)

- `[x]` **6.1** Create `app/main.py`
  - Instantiate `FastAPI` with metadata matching `spec/api-spec.yaml` (title, version, description)
  - Register exception handler for `RequestValidationError` → HTTP 422 `ValidationErrorResponse`
  - Register exception handler for `InvalidTaskInputError` → HTTP 400 `ErrorResponse`
  - Register exception handler for `LLMServiceError` → HTTP 502 `ErrorResponse`
  - Include task router from `app.routes`
  - Define dependency provider functions: `get_llm_service()` and `get_task_repository()`

---

## Phase 7: API Routes (`app/routes.py`)

- `[x]` **7.1** Create `app/routes.py`
  - Define `APIRouter` with prefix `/tasks`
  - Implement `POST /tasks` (`createTask`):
    - Accept `CreateTaskRequest`, inject `BaseLLMService` and `TaskRepository` via `Depends`
    - Call `llm_service.parse_task_from_text(request.input)`
    - Call `task_repository.create(...)` with extracted data
    - Return HTTP 201 with `Task` response
  - Implement `GET /tasks` (`getTasks`):
    - Call `task_repository.get_all()`
    - Return HTTP 200 with `List[Task]` (empty list if no tasks)
  - Implement `GET /tasks/{task_id}` (`getTask`):
    - Path param `task_id: int = Path(..., ge=1)`
    - Return HTTP 200 or raise HTTP 404 `ErrorResponse`
  - Implement `PUT /tasks/{task_id}` (`updateTask`):
    - Accept `UpdateTaskRequest`, update via repository
    - Return HTTP 200 or HTTP 404 `ErrorResponse`
  - Implement `DELETE /tasks/{task_id}` (`deleteTask`):
    - Delete via repository, return HTTP 204 or HTTP 404 `ErrorResponse`
  - Ensure `routes.py` never imports any vendor LLM SDK (zero SDK leakage)

---

## Phase 8: Integration Tests (`tests/test_tasks.py`)

- `[x]` **8.1** Create `tests/__init__.py` (empty)
- `[x]` **8.2** Create `tests/test_tasks.py`
  - Set up `TestClient` with `MockLLMService` override via `app.dependency_overrides`
  - Add `autouse` fixture to call `task_repository.clear()` between tests for isolation
  - Implement the following tests:
    1. `test_create_task_success` — valid input → 201 Created
    2. `test_create_task_empty_input` — `{"input": ""}` → 422
    3. `test_create_task_missing_input_field` — `{}` → 422
    4. `test_create_task_irrelevant_input` — nonsensical input → 400
    5. `test_get_all_tasks_empty` — empty repo → `[]` with 200
    6. `test_get_all_tasks_populated` — multiple tasks → full list with 200
    7. `test_get_task_by_id_success` — existing id → 200 with task
    8. `test_get_task_by_id_not_found` — id 999 → 404 with exact detail string
    9. `test_get_task_invalid_id` — id 0 → 422
    10. `test_update_task_success` — valid update → 200 with updated task
    11. `test_update_task_not_found` — id 999 → 404
    12. `test_update_task_invalid_priority` — `priority: "urgent"` → 422
    13. `test_delete_task_success` — existing id → 204 No Content
    14. `test_delete_task_not_found` — id 999 → 404

---

## Phase 9: LLM Unit Tests (`tests/test_llm.py`)

- `[x]` **9.1** Create `tests/test_llm.py`
  - Implement the following tests:
    1. `test_llm_tool_call_extraction` — structured args extracted correctly from mock tool response
    2. `test_llm_missing_due_date` — tasks without deadlines extract `due_date: None`
    3. `test_llm_priority_inference` — all three priority values (`low`, `medium`, `high`) map correctly
    4. `test_llm_relative_date_resolution` — relative dates resolve to correct `YYYY-MM-DD`
    5. `test_llm_failure_maps_to_502` — LLM error results in 502 with expected detail string
    6. `test_mock_llm_service` — `MockLLMService` satisfies `BaseLLMService` protocol

---

## Phase 10: Documentation

- `[ ]` **10.1** Create `docs/azure-mapping.md`
  - Map each local component to an Azure equivalent:
    - `app/` → Azure App Service / Azure Container Apps
    - `GeminiLLMService` → Azure OpenAI Service
    - `TaskRepository` (in-memory) → Azure Cosmos DB
    - `.env` / API keys → Azure Key Vault
    - Application logging → Azure Application Insights

- `[ ]` **10.2** Create `evaluation/test_cases.json`
  - Include 10+ prompt evaluation test cases covering:
    - Normal cases (clear task with priority and date)
    - Edge cases (relative dates, ambiguous priority, no deadline)
    - Missing-data cases (no priority stated, no date mentioned)
    - Irrelevant / non-task inputs

- `[ ]` **10.3** Create `evaluation/evaluation.md`
  - Document benchmark report on LLM extraction accuracy
  - Include metrics on priority inference accuracy and date handling correctness

- `[ ]` **10.4** Create `README.md`
  - Setup instructions (clone, create venv, install dependencies, set `.env`)
  - Running instructions (`uvicorn app.main:app --reload --port 8000`)
  - Architecture overview diagram (component responsibilities)
  - API usage examples (cURL / Swagger UI)

---

## Phase 11: Verification

- `[ ]` **11.1** Run full pytest suite and confirm all 20 tests pass:
  ```powershell
  pytest -v
  ```
- `[ ]` **11.2** Start the development server and confirm startup with no errors:
  ```powershell
  uvicorn app.main:app --reload --port 8000
  ```
- `[ ]` **11.3** Navigate to `http://localhost:8000/docs` and verify:
  - All 5 routes are listed with correct operationIds
  - Request/response schemas match `spec/api-spec.yaml`
- `[ ]` **11.4** Manually test natural-language task creation via Swagger UI or cURL
- `[ ]` **11.5** Confirm 400, 404, 422, and 502 error responses match the expected schema format
