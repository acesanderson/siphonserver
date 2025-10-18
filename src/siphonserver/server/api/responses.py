"""
StatusResponse,
ConduitResponse,
ConduitError,
SyntheticData,
"""

from conduit.result.response import Response as ConduitResponse
from conduit.result.error import ConduitError
from siphon.data.synthetic_data import SyntheticData
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


class EmbeddingsResponse(BaseModel):
    """Response model for embeddings generation"""

    embeddings: list[list[float]] = Field(
        ..., description="List of generated embeddings"
    )


Responses = {
    "StatusResponse": StatusResponse,
    "ConduitResponse": ConduitResponse,
    "ConduitError": ConduitError,
    "SyntheticData": SyntheticData,
    "EmbeddingsResponse": EmbeddingsResponse,
}
