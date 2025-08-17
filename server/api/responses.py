"""
StatusResponse,
ChainResponse,
ChainError,
SyntheticData,
"""

from Chain.result.response import Response as ChainResponse
from Chain.result.error import ChainError
from Siphon.data.SyntheticData import SyntheticData
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Server status response"""

    status: str = Field(
        ..., description="Server status: 'healthy', 'degraded', 'error'"
    )
    message: str = Field(..., description="Status message")
    models_available: list = Field(..., description="Available models by provider")
    gpu_enabled: bool = Field(..., description="Whether GPU acceleration is available")
    uptime: float | None = Field(None, description="Server uptime in seconds")


Responses = {
    "StatusResponse": StatusResponse,
    "ChainResponse": ChainResponse,
    "ChainError": ChainError,
    "SyntheticData": SyntheticData,
}
