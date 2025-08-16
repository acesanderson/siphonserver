"""
StatusResponse,
ChainResponse,
ChainError,
SyntheticData,
"""

from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Server status response"""

    status: str = Field(
        ..., description="Server status: 'healthy', 'degraded', 'error'"
    )
    message: str = Field(..., description="Status message")
    models_available: dict[str, list[str]] = Field(
        ..., description="Available models by provider"
    )
    gpu_enabled: bool = Field(..., description="Whether GPU acceleration is available")
    uptime: Optional[float] = Field(None, description="Server uptime in seconds")
