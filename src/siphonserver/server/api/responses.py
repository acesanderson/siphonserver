from conduit.result.response import Response as ConduitResponse
from conduit.result.error import ConduitError
from siphon.data.synthetic_data import SyntheticData
from pydantic import BaseModel, Field

# Conduit
# ----- ConduitResponse (imported above) -----
# ----- ConduitError (imported above) -----

# Siphon
# ----- SyntheticData (imported above) -----


# Status
class StatusResponse(BaseModel):
    """Server status response"""

    status: str = Field(
        ..., description="Server status: 'healthy', 'degraded', 'error'"
    )
    message: str = Field(..., description="Status message")
    models_available: list = Field(..., description="Available models by provider")
    gpu_enabled: bool = Field(..., description="Whether GPU acceleration is available")
    uptime: float | None = Field(None, description="Server uptime in seconds")


# Embeddings
class EmbeddingsResponse(BaseModel):
    """Response model for embeddings generation"""

    embeddings: list[list[float]] = Field(
        ..., description="List of generated embeddings"
    )


# Curator
class CuratorResult(BaseModel):
    id: str = Field(..., description="Unique identifier for the curated item")
    score: float = Field(..., description="Curation score for the item")


class CuratorResponse(BaseModel):
    results: list[CuratorResult] = Field(
        ..., description="List of curation results with IDs and scores"
    )


Responses = {
    "StatusResponse": StatusResponse,
    "ConduitResponse": ConduitResponse,
    "ConduitError": ConduitError,
    "SyntheticData": SyntheticData,
    "EmbeddingsResponse": EmbeddingsResponse,
    "CuratorResponse": CuratorResponse,
    "CuratorResult": CuratorResult,
}
