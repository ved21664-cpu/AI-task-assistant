# AI-Powered Task Assistant API — Requirements Specification

## 1. Problem Statement

Users often describe tasks using natural language rather than structured task fields.

For example:

> "Remind me to submit the project report by Friday and mark it as high priority."

A traditional task management API expects structured information such as a title, description, priority, and due date. This requires the user to manually provide each field.

The AI-Powered Task Assistant API will solve this problem by accepting a user's natural-language task request and using a Large Language Model (LLM) to convert the request into a structured task object.

The system will expose this functionality through a FastAPI backend and will provide APIs for creating, retrieving, updating, and deleting tasks.

The application will use an in-memory data store, so a persistent database is not required for this assignment.

---

## 2. Functional Requirements

### FR-01 — Natural-Language Task Input

The system shall accept a user's task description in natural language and process it to create a structured task object.

Example:

```text
"Submit the project report by Friday and mark it as high priority."
```

### FR-02 — Structured Task Generation

The system shall use an LLM to convert the natural-language task description into a structured task containing:

* title
* description
* priority
* due date

The priority shall be one of:

```text
low
medium
high
```

The due date shall use the format:

```text
YYYY-MM-DD
```

or `null` when a due date is not available.

### FR-03 — Create Task

The system shall provide an API endpoint that allows a user to create a task from a natural-language request.

```text
POST /tasks
```

The actual creation and storage of the task shall be performed by the Python application rather than directly by the LLM.

### FR-04 — Retrieve All Tasks

The system shall provide an API endpoint that returns all tasks currently stored by the application.

```text
GET /tasks
```

### FR-05 — Retrieve a Specific Task

The system shall provide an API endpoint that retrieves a specific task using its task ID.

```text
GET /tasks/{task_id}
```

### FR-06 — Update a Task

The system shall provide an API endpoint that allows an existing task to be updated.

```text
PUT /tasks/{task_id}
```

### FR-07 — Delete a Task

The system shall provide an API endpoint that allows an existing task to be deleted.

```text
DELETE /tasks/{task_id}
```

### FR-08 — Function/Tool Calling

The system shall implement at least one function or tool that the LLM can invoke.

The function shall accept structured task information and allow the Python application to perform the corresponding task operation.

For example:

```text
create_task(
    title,
    description,
    priority,
    due_date
)
```

The LLM shall determine when the function should be invoked and provide the required structured arguments.

### FR-09 — Input and Output Validation

The system shall validate API inputs and structured task data using Pydantic models.

Invalid values, such as an unsupported priority, shall not be accepted as valid task data.

### FR-10 — API Documentation

The system shall expose interactive API documentation through FastAPI.

The API shall document the available endpoints, request bodies, response bodies, parameters, and applicable HTTP status codes.

---

## 3. Non-Functional Requirements

### NFR-01 — Asynchronous Execution

The system shall use asynchronous Python (`async`/`await`) for appropriate I/O-bound operations, including communication with the external LLM API.

### NFR-02 — Separation of Concerns

The application shall separate API routes, business logic, LLM integration, data validation, and data storage.

The API layer shall not contain provider-specific LLM implementation details.

### NFR-03 — LLM Provider Abstraction

The LLM integration shall be abstracted so that the application can switch between supported LLM providers without requiring changes to the core FastAPI or business-logic layers.

### NFR-04 — Secure Credential Management

The application shall obtain LLM API credentials from environment variables or another secure configuration mechanism.

API keys and other credentials shall never be hard-coded in source code or committed to the Git repository.

### NFR-05 — Error Handling

The API shall handle invalid input, missing resources, invalid LLM output, and LLM/API failures gracefully and return appropriate HTTP responses.

### NFR-06 — Testability

The application shall be structured so that individual components can be tested independently using `pytest`.

LLM-dependent tests should be capable of using mocked LLM responses where appropriate.

---

## 4. User Flow

### 4.1 Create a Task

The primary user flow is:

```text
User
  |
  | Natural-language task request
  v
FastAPI
  |
  v
Task Service
  |
  v
LLM Service
  |
  v
LLM
  |
  | Structured task information
  v
Pydantic Validation
  |
  v
Task Creation Function
  |
  v
Task Repository
  |
  v
Stored Task
  |
  v
API Response
  |
  v
User
```

### Example

The user sends:

```text
"Remind me to submit the project report by Friday and mark it as high priority."
```

The LLM should produce structured information similar to:

```json
{
  "title": "Submit project report",
  "description": "Submit the project report",
  "priority": "high",
  "due_date": "2026-08-21"
}
```

The Python application validates this information and creates the task.

### 4.2 Retrieve Tasks

```text
User
  |
  | GET /tasks
  v
FastAPI
  |
  v
Task Repository
  |
  v
List of Tasks
  |
  v
User
```

### 4.3 Retrieve a Specific Task

```text
User
  |
  | GET /tasks/{task_id}
  v
FastAPI
  |
  v
Task Repository
  |
  v
Requested Task
  |
  v
User
```

### 4.4 Update a Task

```text
User
  |
  | PUT /tasks/{task_id}
  v
FastAPI
  |
  v
Validation
  |
  v
Task Repository
  |
  v
Updated Task
  |
  v
User
```

### 4.5 Delete a Task

```text
User
  |
  | DELETE /tasks/{task_id}
  v
FastAPI
  |
  v
Task Repository
  |
  v
Task Deleted
  |
  v
User
```

---

## 5. Expected Inputs and Outputs

### 5.1 Create Task Input

The API shall accept a natural-language task description.

Example:

```json
{
  "input": "Submit my project report by Friday and make it high priority."
}
```

### 5.2 Structured LLM Output

The LLM is expected to produce:

```json
{
  "title": "Submit project report",
  "description": "Submit the project report",
  "priority": "high",
  "due_date": "2026-08-21"
}
```

The expected schema is:

```json
{
  "title": "string",
  "description": "string",
  "priority": "low | medium | high",
  "due_date": "YYYY-MM-DD | null"
}
```

### 5.3 Stored Task Output

After the Python application creates the task, the stored task shall additionally contain a unique task ID.

Example:

```json
{
  "id": 1,
  "title": "Submit project report",
  "description": "Submit the project report",
  "priority": "high",
  "due_date": "2026-08-21"
}
```

### 5.4 Retrieve Tasks Output

A successful `GET /tasks` request shall return a collection of stored tasks.

Example:

```json
[
  {
    "id": 1,
    "title": "Submit project report",
    "description": "Submit the project report",
    "priority": "high",
    "due_date": "2026-08-21"
  }
]
```

---

## 6. Error Cases and Edge Cases

### EC-01 — Empty Task Request

If the user submits an empty or invalid task description, the system shall reject the request and return an appropriate validation error.

Example:

```json
{
  "input": ""
}
```

### EC-02 — Non-Existent Task

If a user requests, updates, or deletes a task ID that does not exist, the system shall return an appropriate not-found response.

Example:

```text
GET /tasks/999
```

when task `999` does not exist.

### EC-03 — Invalid Priority

If the LLM or user-provided data contains a priority outside the supported values:

```text
low
medium
high
```

the system shall reject the invalid value.

Example:

```json
{
  "priority": "urgent"
}
```

### EC-04 — Invalid Due Date

If the LLM produces a due date that does not follow the expected date format, the system shall reject or appropriately handle the invalid date.

Example:

```text
due_date = "tomorrow"
```

instead of:

```text
due_date = "2026-08-21"
```

### EC-05 — Missing Information

If the natural-language request does not contain optional information such as a due date, the system shall represent the missing value appropriately rather than inventing information.

Example:

```text
"Buy groceries."
```

may produce:

```json
{
  "title": "Buy groceries",
  "description": "Buy groceries",
  "priority": "medium",
  "due_date": null
}
```

The LLM shall not hallucinate a deadline that the user did not provide.

### EC-06 — Invalid LLM Output

If the LLM returns malformed, incomplete, or otherwise invalid structured output, the application shall validate the response and handle the failure gracefully.

### EC-07 — LLM/API Failure

If the external LLM API is unavailable or returns an error, the application shall handle the failure without crashing the FastAPI application.

### EC-08 — Ambiguous User Request

If the user's request is ambiguous or does not contain enough information to reliably determine a task field, the system shall avoid inventing information and handle the missing information according to the defined task schema.

### EC-09 — Irrelevant Input

If the user provides input that does not describe a task, the system shall handle the input gracefully rather than creating a task containing fabricated information.

---

## 7. Assumptions

1. The application is intended for local development and demonstration as part of the Week 1 assignment.

2. An external LLM API will be used for natural-language understanding and structured task generation.

3. Gemini 2.5 Flash is the recommended LLM, but the application should allow the LLM provider to be replaced.

4. The LLM provider will support text generation, structured/JSON output, and function/tool calling.

5. The application will use an in-memory data store.

6. Persistent database storage is not required.

7. Tasks are represented using a unique task ID, title, description, priority, and optional due date.

8. Supported task priorities are limited to:

   * low
   * medium
   * high

9. Dates are represented using the `YYYY-MM-DD` format.

10. The application will use environment variables for API credentials.

11. The system does not need to deploy to Azure for this assignment.

12. Unit tests may use mocked LLM responses rather than making real external API calls.

---

## 8. Out-of-Scope Functionality

The following functionality is outside the scope of this assignment:

### 8.1 User Authentication

User registration, login, authentication, authorization, and user accounts will not be implemented.

### 8.2 Persistent Database

A production database such as PostgreSQL or another persistent database system is not required.

### 8.3 Notifications and Reminders

The system will structure due dates but will not actually send email, SMS, push notifications, or reminders.

### 8.4 Calendar Integration

Integration with Google Calendar, Outlook Calendar, or other calendar systems is not required.

### 8.5 Production Azure Deployment

The application does not need to be deployed to Azure. Azure integration is limited to architectural service mapping.

### 8.6 Advanced Task Management

Features such as recurring tasks, task categories, tags, subtasks, attachments, collaboration, and task sharing are outside the scope.

### 8.7 Production-Scale Infrastructure

Load balancing, horizontal scaling, Kubernetes orchestration, distributed databases, and other production infrastructure are not required.

### 8.8 Advanced LLM Features

The application will not implement conversational memory, multi-agent workflows, autonomous task planning, or other advanced AI-agent capabilities beyond the required structured output and function/tool calling.

---

## 9. Success Criteria

The implementation will be considered successful when:

1. The FastAPI application runs locally.
2. A natural-language task request can be converted into a structured task.
3. The API supports task creation, retrieval, updating, and deletion.
4. Pydantic validation is implemented.
5. At least one LLM function/tool can be invoked.
6. The LLM integration is separated from the API/business-logic layer.
7. At least 10 prompt evaluation cases have been completed.
8. At least 10 meaningful unit tests have been implemented.
9. All automated tests pass.
10. API documentation is available through FastAPI.
11. Azure service mapping is documented.
12. No API keys or secrets are committed to the repository.
13. The project contains setup, architecture, and usage documentation in `README.md`.
