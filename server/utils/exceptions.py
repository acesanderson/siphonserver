# app/utils/exceptions.py
from typing import Optional


class ServerError(Exception):
    """Base exception for server errors"""

    def __init__(
        self, message: str, status_code: int = 500, code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code or "server_error"
        super().__init__(self.message)


class ModelNotFoundError(ServerError):
    """Raised when requested model is not available"""

    def __init__(self, model_name: str):
        super().__init__(
            message=f"Model '{model_name}' not found or not available",
            status_code=404,
            code="model_not_found",
        )


class BatchSizeError(ServerError):
    """Raised when batch size exceeds limits"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"Batch size {size} exceeds maximum allowed size {max_size}",
            status_code=400,
            code="batch_size_exceeded",
        )


class InvalidRequestError(ServerError):
    """Raised for malformed requests"""

    def __init__(self, details: str):
        super().__init__(
            message=f"Invalid request: {details}",
            status_code=400,
            code="invalid_request",
        )
