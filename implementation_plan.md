# Implementation Plan — AI-Powered Task Assistant API

## Overview
This implementation plan outlines the architectural design, component responsibilities, schemas, routes, repository layer, LLM integration, tool calling mechanisms, testing strategy, and specification analysis for the **AI-Powered Task Assistant API** based on `spec/requirements.md` and `spec/api-spec.yaml`.

---

## 1. Requirements-to-Files Traceability Matrix

| Requirement ID | Description | Implementing Files |
| :--- | :--- | :--- |
| **FR-01** | Natural-Language Task Input | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/schemas.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/schemas.py), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **FR-02** | Structured Task Generation (title, description, priority, due_date) | [app/schemas.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/schemas.py), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **FR-03** | Create Task (`POST /tasks`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **FR-04** | Retrieve All Tasks (`GET /tasks`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py) |
| **FR-05** | Retrieve a Specific Task (`GET /tasks/{task_id}`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py) |
| **FR-06** | Update a Task (`PUT /tasks/{task_id}`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py) |
| **FR-07** | Delete a Task (`DELETE /tasks/{task_id}`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py) |
| **FR-08** | Function/Tool Calling | [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **FR-09** | Input & Output Validation | [app/schemas.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/schemas.py), [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py) |
| **FR-10** | Interactive API Documentation | [app/main.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/main.py) |
| **NFR-01** | Asynchronous Execution (`async`/`await`) | [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **NFR-02** | Separation of Concerns | Entire codebase architecture (`routes`, `services`, `repository`, `schemas`, `models`) |
| **NFR-03** | LLM Provider Abstraction | [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) (Base class / Protocol) |
| **NFR-04** | Secure Credential Management | [.env](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/.env), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py), [app/main.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/main.py) |
| **NFR-05** | Error Handling & Status Codes (400, 404, 422, 502) | [app/main.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/main.py), [app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py), [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py) |
| **NFR-06** | Testability & Pytest Support | [tests/test_tasks.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/tests/test_tasks.py), [tests/test_llm.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/tests/test_llm.py) |
| **Doc/Eval** | Azure Service Mapping | [docs/azure-mapping.md](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/docs/azure-mapping.md) |
| **Doc/Eval** | Prompt Evaluation & Benchmark (10+ cases) | [evaluation/test_cases.json](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/evaluation/test_cases.json), [evaluation/evaluation.md](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/evaluation/evaluation.md) |
| **Doc/Eval** | Project Documentation & Setup Guide | [README.md](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/README.md) |

---

## 2. File Responsibilities in the Project Directory

```
AI task assistant/
├── app/
│   ├── main.py                  # App initialization, OpenAPI metadata, exception handlers, router inclusion
│   ├── models.py                # Internal domain dataclasses / models for task storage
│   ├── schemas.py               # Pydantic schemas for request/response serialization and validation
│   ├── routes.py                # FastAPI HTTP route handlers for /tasks and /tasks/{task_id}
│   ├── repository/
│   │   └── task_repository.py   # In-memory CRUD data store and atomic ID generator
│   └── services/
│       └── llm_service.py       # LLM provider interface, Gemini implementation, tool definitions & parser
├── docs/
│   └── azure-mapping.md         # Enterprise Azure cloud architecture mapping document
├── evaluation/
│   ├── test_cases.json          # 10+ prompt evaluation test cases covering normal, edge, and missing-data scenarios
│   └── evaluation.md            # Benchmark report and accuracy metrics for LLM task extraction
├── spec/
│   ├── api-spec.yaml            # OpenAPI 3.0.3 specification
│   └── requirements.md          # Functional, Non-Functional, and Out-of-Scope requirements
├── tests/
│   ├── test_tasks.py            # Integration tests for CRUD routes, validation, and status codes
│   └── test_llm.py              # Unit tests for LLMService, mock provider, tool calling, and error translation
├── .env                         # Local environment variables (GEMINI_API_KEY)
├── .gitignore                   # Ignore .env, __pycache__, .pytest_cache, virtual environments
├── README.md                    # Setup, running instructions, architecture overview, and API examples
└── requirements.txt             # Python dependencies (fastapi, uvicorn, pydantic, google-genai, pytest, httpx, python-dotenv)
```

### Detailed Responsibility of Each File:
1. **[app/main.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/main.py)**:
   - Configures the FastAPI app instance with metadata (title, version, description matching `api-spec.yaml`).
   - Registers custom exception handlers for `RequestValidationError` (returning HTTP 422 with the exact `ValidationErrorResponse` schema) and custom domain exceptions (e.g., `LLMServiceError` returning HTTP 502 `ErrorResponse`, `InvalidTaskInputError` returning HTTP 400).
   - Includes the task routes from `app.routes`.
2. **[app/models.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/models.py)**:
   - Defines internal domain representations (such as `TaskModel` dataclass) decoupled from HTTP request/response DTOs.
3. **[app/schemas.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/schemas.py)**:
   - Houses all Pydantic v2 validation models for input requests, output responses, enums, tool call schemas, and error responses.
4. **[app/routes.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/routes.py)**:
   - Exposes REST endpoints (`POST /tasks`, `GET /tasks`, `GET /tasks/{task_id}`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}`).
   - Orchestrates requests: receives validated Pydantic models, delegates AI extraction to `LLMService`, interacts with `TaskRepository`, and returns HTTP status codes (200, 201, 204, 400, 404, 422, 502).
5. **[app/repository/task_repository.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/repository/task_repository.py)**:
   - Manages the in-memory data store (`dict[int, TaskModel]`), provides atomic ID auto-incrementing, and implements `create`, `get_all`, `get_by_id`, `update`, `delete`, and `clear` methods.
6. **[app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py)**:
   - Declares the `LLMService` abstract base class/protocol.
   - Defines the `create_task` tool declaration for function calling.
   - Implements `GeminiLLMService` using Google GenAI SDK (with date anchoring and error translation) and `MockLLMService` for deterministic offline testing.
7. **[tests/test_tasks.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/tests/test_tasks.py)**:
   - Pytest suite using `TestClient` / `AsyncClient` to test all CRUD routes, status codes, validations, and edge cases.
8. **[tests/test_llm.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/tests/test_llm.py)**:
   - Unit test suite for `LLMService` parsing, tool calling logic, date parsing, and failure recovery.
9. **[docs/azure-mapping.md](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/docs/azure-mapping.md)**:
   - Architecture mapping comparing local components to Azure App Service / Container Apps, Azure OpenAI, Azure Cosmos DB, Azure Key Vault, and Application Insights.
10. **[evaluation/test_cases.json](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/evaluation/test_cases.json)** & **[evaluation/evaluation.md](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/evaluation/evaluation.md)**:
    - 10+ evaluation test cases and analytical report on extraction accuracy, priority inference, and date handling.

---

## 3. Pydantic Models and Schemas

To satisfy both `spec/requirements.md` and `spec/api-spec.yaml`, the following schemas are required:

```python
from enum import Enum
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from datetime import date

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CreateTaskRequest(BaseModel):
    input: str = Field(
        ...,
        min_length=1,
        description="Natural-language description of the task",
        example="Submit my project report by Friday and make it high priority."
    )

class UpdateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Task title", example="Submit final project report")
    description: str = Field(..., min_length=1, description="Task description", example="Submit the completed project report")
    priority: PriorityEnum = Field(..., description="Task priority", example=PriorityEnum.HIGH)
    due_date: Optional[date] = Field(None, description="Task due date. May be null when no deadline exists.", example="2026-08-22")

class Task(BaseModel):
    id: int = Field(..., ge=1, description="Unique task identifier", example=1)
    title: str = Field(..., description="Task title", example="Submit project report")
    description: str = Field(..., description="Task description", example="Submit the project report")
    priority: PriorityEnum = Field(..., description="Task priority", example=PriorityEnum.HIGH)
    due_date: Optional[date] = Field(None, description="Task due date", example="2026-08-21")

class ExtractedTaskData(BaseModel):
    """Schema representing structured data extracted by the LLM via tool calling."""
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM, description="Task priority")
    due_date: Optional[date] = Field(default=None, description="Due date in YYYY-MM-DD format or null")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable description of the error", example="Task with id 999 not found")

class ValidationError(BaseModel):
    loc: List[Union[str, int]] = Field(..., description="Location of the validation error", example=["body", "priority"])
    msg: str = Field(..., description="Validation error message", example="Input should be 'low', 'medium' or 'high'")
    type: str = Field(..., description="Type of validation error", example="enum")

class ValidationErrorResponse(BaseModel):
    detail: List[ValidationError]
```

---

## 4. API Routes Required

All routes conform to the OpenAPI 3.0.3 specification in `spec/api-spec.yaml`:

### 1. `POST /tasks` — Create Task from Natural Language
- **OperationId**: `createTask`
- **Request Body**: `CreateTaskRequest` (JSON with `input: str`)
- **Responses**:
  - `201 Created`: Returns `Task`
  - `400 Bad Request`: Returns `ErrorResponse` (detail: `"Invalid task input"`)
  - `422 Unprocessable Entity`: Returns `ValidationErrorResponse`
  - `502 Bad Gateway`: Returns `ErrorResponse` (detail: `"Unable to process task using the LLM service"`)

### 2. `GET /tasks` — Retrieve All Tasks
- **OperationId**: `getTasks`
- **Request**: None
- **Responses**:
  - `200 OK`: Returns `List[Task]` (empty list `[]` if no tasks exist)

### 3. `GET /tasks/{task_id}` — Retrieve Specific Task
- **OperationId**: `getTask`
- **Path Parameter**: `task_id: int` (minimum: 1)
- **Responses**:
  - `200 OK`: Returns `Task`
  - `404 Not Found`: Returns `ErrorResponse` (detail: `"Task with id {task_id} not found"`)
  - `422 Unprocessable Entity`: Returns `ValidationErrorResponse` (e.g. `task_id < 1`)

### 4. `PUT /tasks/{task_id}` — Update Task
- **OperationId**: `updateTask`
- **Path Parameter**: `task_id: int` (minimum: 1)
- **Request Body**: `UpdateTaskRequest`
- **Responses**:
  - `200 OK`: Returns updated `Task`
  - `404 Not Found`: Returns `ErrorResponse` (detail: `"Task with id {task_id} not found"`)
  - `422 Unprocessable Entity`: Returns `ValidationErrorResponse`

### 5. `DELETE /tasks/{task_id}` — Delete Task
- **OperationId**: `deleteTask`
- **Path Parameter**: `task_id: int` (minimum: 1)
- **Responses**:
  - `204 No Content`: Empty body
  - `404 Not Found`: Returns `ErrorResponse` (detail: `"Task with id {task_id} not found"`)
  - `422 Unprocessable Entity`: Returns `ValidationErrorResponse`

---

## 5. Repository Layer Methods (`TaskRepository`)

The `TaskRepository` maintains an in-memory dictionary store (`dict[int, TaskModel]`) with an auto-incrementing integer sequence:

```python
class TaskRepository:
    def __init__(self):
        self._tasks: dict[int, TaskModel] = {}
        self._counter: int = 1

    def create(self, title: str, description: str, priority: PriorityEnum, due_date: Optional[date]) -> TaskModel:
        """Assigns auto-increment ID, stores task, and returns created TaskModel."""
        ...

    def get_all(self) -> list[TaskModel]:
        """Returns list of all stored TaskModel instances."""
        ...

    def get_by_id(self, task_id: int) -> Optional[TaskModel]:
        """Returns TaskModel if found, else None."""
        ...

    def update(self, task_id: int, update_data: UpdateTaskRequest) -> Optional[TaskModel]:
        """Updates existing task fields and returns updated TaskModel, or None if not found."""
        ...

    def delete(self, task_id: int) -> bool:
        """Deletes task by ID. Returns True if deleted, False if not found."""
        ...

    def clear(self) -> None:
        """Clears all tasks and resets counter (used for test isolation)."""
        ...
```

---

## 6. LLM Service Responsibilities

The `LLMService` is responsible for:
1. **Prompt Engineering & Temporal Anchoring**: Injecting the current system/UTC date (e.g. `Today is Friday, 2026-08-21`) so the LLM accurately computes relative deadlines ("tomorrow", "next Monday", "by Friday").
2. **Tool / Function Declaration**: Exposing the `create_task` tool schema to the LLM.
3. **Structured Argument Extraction**: Invoking the LLM with tool calling enabled, parsing the tool arguments from the model response, and validating them against `ExtractedTaskData`.
4. **Input Guardrails & Irrelevant Input Detection**: Detecting when user input cannot produce a sensible task, raising an `InvalidTaskInputError` (mapped to HTTP 400).
5. **Resilient Error Translation**: Catching SDK network errors, rate limits, authentication failures, or invalid JSON, and raising domain-specific `LLMServiceError` (mapped to HTTP 502).

---

## 7. LLM Integration Separation from the API Layer

To strictly satisfy **NFR-02 (Separation of Concerns)** and **NFR-03 (LLM Provider Abstraction)**:

```
[HTTP Request] -> [FastAPI Route in routes.py]
                        | (injects via Depends)
                        v
              [BaseLLMService Interface]
              /                        \
    [GeminiLLMService]            [MockLLMService]
    (Google GenAI SDK)            (Unit Test Stub)
            |                             |
            v                             v
    [ExtractedTaskData]           [ExtractedTaskData]
            |
            v
    [TaskRepository.create()]
            |
            v
    [HTTP 201 Response with Task]
```

- **Abstract Interface**: `BaseLLMService` defines an asynchronous method:
  `async def parse_task_from_text(self, text: str) -> ExtractedTaskData`
- **Zero SDK Leakage in Routes**: `routes.py` never imports `google-genai` or vendor SDKs. It only interacts with `BaseLLMService` and domain exceptions.
- **FastAPI Dependency Injection**: `get_llm_service()` and `get_task_repository()` provide instances via `Depends()`. Tests can easily override `app.dependency_overrides[get_llm_service]` with `MockLLMService`.

---

## 8. Function / Tool Calling Implementation Plan

Function calling is implemented directly within [app/services/llm_service.py](file:///c:/Users/VedAtulyaKamat/OneDrive%20-%20McLaren%20Strategic%20Solutions%20US%20Inc/AI%20task%20assistant/app/services/llm_service.py):

### Tool Definition
The `create_task` tool definition provided to the Gemini model:
```json
{
  "name": "create_task",
  "description": "Create a structured task object from natural language task descriptions.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Short, clear title summarizing the task"
      },
      "description": {
        "type": "string",
        "description": "Full description of the task"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Priority level. Default to medium if unspecified."
      },
      "due_date": {
        "type": "string",
        "description": "Due date in YYYY-MM-DD format, or null if no deadline is mentioned"
      }
    },
    "required": ["title", "description", "priority"]
  }
}
```

### Execution Flow:
1. User provides: `"Submit the project report by Friday and mark it as high priority."`
2. `LLMService` sends system prompt with tool declaration and current date reference.
3. LLM responds with a tool call `create_task(title="Submit project report", description="Submit the project report", priority="high", due_date="2026-08-21")`.
4. `LLMService` extracts and validates the tool call arguments into `ExtractedTaskData`.
5. The Python application (route handler) calls `TaskRepository.create(...)` with the extracted data to assign an ID and persist the task in memory.

---

## 9. Comprehensive Testing Strategy

A minimum of 10+ automated tests will be implemented across two test modules:

### 1. `tests/test_tasks.py` (API & Repository Integration Tests)
1. `test_create_task_success`: `POST /tasks` with valid input creates task (201 Created).
2. `test_create_task_empty_input`: `POST /tasks` with `{"input": ""}` returns 422.
3. `test_create_task_missing_input_field`: `POST /tasks` with `{}` returns 422.
4. `test_create_task_irrelevant_input`: `POST /tasks` with nonsensical input returns 400 Bad Request.
5. `test_get_all_tasks_empty`: `GET /tasks` on empty repository returns `[]` with 200 OK.
6. `test_get_all_tasks_populated`: `GET /tasks` with multiple items returns full list.
7. `test_get_task_by_id_success`: `GET /tasks/{id}` returns the specific task with 200 OK.
8. `test_get_task_by_id_not_found`: `GET /tasks/999` returns 404 with exact error detail.
9. `test_get_task_invalid_id`: `GET /tasks/0` returns 422 (path param validation).
10. `test_update_task_success`: `PUT /tasks/{id}` updates fields and returns 200 OK.
11. `test_update_task_not_found`: `PUT /tasks/999` returns 404.
12. `test_update_task_invalid_priority`: `PUT /tasks/{id}` with `priority: "urgent"` returns 422.
13. `test_delete_task_success`: `DELETE /tasks/{id}` returns 204 No Content.
14. `test_delete_task_not_found`: `DELETE /tasks/999` returns 404.

### 2. `tests/test_llm.py` (LLM Service Unit Tests)
1. `test_llm_tool_call_extraction`: Validates extraction of structured arguments from mock tool response.
2. `test_llm_missing_due_date`: Validates that tasks without deadlines extract `due_date: None` without hallucinations.
3. `test_llm_priority_inference`: Verifies priority mapping (`low`, `medium`, `high`).
4. `test_llm_relative_date_resolution`: Verifies relative dates ("tomorrow", "by Friday") correctly resolve to `YYYY-MM-DD`.
5. `test_llm_failure_maps_to_502`: When LLM provider fails/times out, `POST /tasks` returns 502 with detail `"Unable to process task using the LLM service"`.
6. `test_mock_llm_service`: Verifies mock service matches `BaseLLMService` protocol.

---

## 10. Ambiguities and Conflicts Identified in the Specifications

1. **Validation Error Codes for `POST /tasks` (400 vs 422)**:
   - *Ambiguity*: In `requirements.md` EC-01, empty input is described as returning a validation error. In `api-spec.yaml`, both `400` ("Invalid task input") and `422` ("Request validation error") are defined.
   - *Resolution*: Pydantic schema validation failures (e.g. `input` field missing or `input: ""`) return HTTP 422 matching `ValidationErrorResponse`. Logical task validation failures (e.g. input string that cannot be interpreted as a task) will return HTTP 400 `ErrorResponse(detail="Invalid task input")`.
2. **Date Serialization & Nullability**:
   - *Ambiguity*: `api-spec.yaml` specifies `due_date` as `type: string, format: date, nullable: true`.
   - *Resolution*: Pydantic model will use `Optional[date] = None`, ensuring dates are serialized as `YYYY-MM-DD` strings or JSON `null`, preventing string mismatches.
3. **Temporal Anchoring for Relative Dates**:
   - *Ambiguity*: `requirements.md` mentions inputs like "by Friday" without specifying the current execution date.
   - *Resolution*: The prompt must dynamically inject the current execution date into the system instructions so relative dates are deterministically computed.
4. **404 Not Found Detail Consistency**:
   - *Ambiguity*: `api-spec.yaml` examples use `"Task with id 1 not found"` and `"Task with id 999 not found"`.
   - *Resolution*: All repository lookups across `GET`, `PUT`, `DELETE` will consistently format the detail string as `f"Task with id {task_id} not found"`.
5. **Path Parameter Minimum Constraint**:
   - *Ambiguity*: `api-spec.yaml` defines `task_id` with `minimum: 1`.
   - *Resolution*: In FastAPI, declaring `task_id: int = Path(..., ge=1)` produces a 422 Unprocessable Entity error when `task_id <= 0`, adhering to `api-spec.yaml`.

---

## Verification Plan

### Automated Tests
- Run full pytest test suite:
  ```powershell
  pytest -v
  ```

### Manual Verification
- Start development server:
  ```powershell
  uvicorn app.main:app --reload --port 8000
  ```
- Inspect OpenAPI documentation at `http://localhost:8000/docs`.
- Test natural language task creation, retrieval, update, and deletion via Swagger UI / cURL.
