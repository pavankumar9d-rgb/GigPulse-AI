"""Standard error formatting and exception handlers conforming to docs/06_API_CONTRACT.md."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    """Custom application exception with structured error code and details."""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id or f"req_{uuid.uuid4().hex[:8]}",
                "details": details or [],
            }
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return build_error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = []
        for err in exc.errors():
            loc = ".".join(str(l) for l in err.get("loc", []))
            details.append({"field": loc, "reason": err.get("msg", "Invalid value")})
        return build_error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request body or query parameter validation failed.",
            details=details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            404: "NOT_FOUND",
            400: "BAD_REQUEST",
            403: "FORBIDDEN",
            401: "UNAUTHORIZED",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        return build_error_response(
            status_code=exc.status_code,
            code=code,
            message=str(exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Never expose internal stack traces or secrets
        return build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please try again later.",
        )
