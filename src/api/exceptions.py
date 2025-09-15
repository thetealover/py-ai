import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(exc: StarletteHTTPException):
    """
    Global handler for FastAPI's HTTPException.
    Ensures that all manually raised HTTPErrors return a consistent JSON format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global handler for Pydantic's RequestValidationError.
    This triggers when request data is invalid. It formats the default
    error response into a cleaner, more developer-friendly structure.
    """
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        errors.append({"field": field_path, "message": error["msg"]})

    logger.warning(f"Request validation failed for {request.url}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Global handler for any unhandled exceptions (catch-all).
    Logs the full traceback for debugging but returns a generic 500 error
    to the client to avoid leaking implementation details.
    """
    logger.error(
        f"Unhandled exception for request: {request.method} {request.url}",
        exc_info=exc
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


def register_exception_handlers(app):
    """
    Registers all custom exception handlers with the FastAPI app instance.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    logger.info("Global exception handlers have been registered.")
