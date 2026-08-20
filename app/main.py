"""
app/main.py
FastAPI application initialization, metadata, exception handlers, and router registration.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.dependencies import get_llm_service, get_task_repository  # noqa: F401 — re-exported for tests
from app.services.llm_service import InvalidTaskInputError, LLMServiceError

# Initialize FastAPI application with OpenAPI 3.0.3 specification metadata
app = FastAPI(
    title="AI-Powered Task Assistant API",
    description=(
        "REST API for creating and managing tasks using natural-language input. "
        "The API uses an LLM to convert natural-language task descriptions into "
        "structured task objects."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Custom Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats 422 validation errors to strictly conform to ValidationErrorResponse schema."""
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append(
            {
                "loc": list(error.get("loc", [])),
                "msg": error.get("msg", "Validation error"),
                "type": error.get("type", "value_error"),
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors},
    )


@app.exception_handler(InvalidTaskInputError)
async def invalid_task_input_exception_handler(request: Request, exc: InvalidTaskInputError) -> JSONResponse:
    """Formats 400 Bad Request error when natural language input is not actionable."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message or "Invalid task input"},
    )


@app.exception_handler(LLMServiceError)
async def llm_service_exception_handler(request: Request, exc: LLMServiceError) -> JSONResponse:
    """Formats 502 Bad Gateway error when LLM provider fails."""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "Unable to process task using the LLM service"},
    )


# ---------------------------------------------------------------------------
# Router Registration (imported here to avoid circular import with dependencies.py)
# ---------------------------------------------------------------------------

from app.routes import router as tasks_router  # noqa: E402
app.include_router(tasks_router)
