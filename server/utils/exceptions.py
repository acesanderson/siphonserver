from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
import traceback
import time


class ErrorType(str, Enum):
    VALIDATION_ERROR = "validation_error"
    PYDANTIC_VALIDATION = "pydantic_validation"
    DATA_VALIDATION = "data_validation"
    MODEL_NOT_FOUND = "model_not_found"
    BATCH_SIZE_EXCEEDED = "batch_size_exceeded"
    INVALID_REQUEST = "invalid_request"
    INTERNAL_ERROR = "internal_error"
    TIMEOUT_ERROR = "timeout_error"
    DEPENDENCY_ERROR = "dependency_error"


class SiphonServerError(BaseModel):
    """Centralized error response format for SiphonServer"""

    # Core error info
    error_type: ErrorType
    message: str
    status_code: int = Field(ge=100, le=599)

    # Request context
    path: Optional[str] = None
    method: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

    # Detailed error information
    validation_errors: Optional[list[dict[str, Any]]] = None
    original_exception: Optional[str] = None
    traceback: Optional[str] = None

    # Additional context
    context: Optional[dict[str, Any]] = Field(default_factory=dict)

    @classmethod
    def from_validation_error(
        cls, exc, request=None, include_traceback: bool = False
    ) -> "SiphonServerError":
        """Create error from Pydantic ValidationError"""
        return cls(
            error_type=ErrorType.PYDANTIC_VALIDATION,
            message="Request validation failed",
            status_code=422,
            path=str(request.url.path) if request else None,
            method=request.method if request else None,
            request_id=getattr(request.state, "request_id", None) if request else None,
            validation_errors=exc.errors() if hasattr(exc, "errors") else None,
            original_exception=str(exc),
            traceback=traceback.format_exc() if include_traceback else None,
        )

    @classmethod
    def from_http_exception(
        cls, exc, request=None, error_type: ErrorType = ErrorType.INTERNAL_ERROR
    ) -> "SiphonServerError":
        """Create error from HTTPException"""
        return cls(
            error_type=error_type,
            message=str(exc.detail) if hasattr(exc, "detail") else str(exc),
            status_code=getattr(exc, "status_code", 500),
            path=str(request.url.path) if request else None,
            method=request.method if request else None,
            request_id=getattr(request.state, "request_id", None) if request else None,
            original_exception=str(exc),
        )

    @classmethod
    def from_general_exception(
        cls,
        exc: Exception,
        request=None,
        status_code: int = 500,
        include_traceback: bool = True,
    ) -> "SiphonServerError":
        """Create error from any exception"""
        return cls(
            error_type=ErrorType.INTERNAL_ERROR,
            message=f"Internal server error: {str(exc)}",
            status_code=status_code,
            path=str(request.url.path) if request else None,
            method=request.method if request else None,
            request_id=getattr(request.state, "request_id", None) if request else None,
            original_exception=str(exc),
            traceback=traceback.format_exc() if include_traceback else None,
            context={"exception_type": type(exc).__name__},
        )

    def add_context(self, key: str, value: Any) -> "SiphonServerError":
        """Add additional context information"""
        if self.context is None:
            self.context = {}
        self.context[key] = value
        return self
