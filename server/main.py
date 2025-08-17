"""
Main orchestrator for the Siphon & Chain API server.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
import time

# Project Imports
## Models
from SiphonServer.server.api.requests import (
    ChainRequest,
    BatchRequest,
    SyntheticDataRequest,
)
from SiphonServer.server.api.responses import (
    StatusResponse,
    ChainResponse,
    ChainError,
    SyntheticData,
)

## Utils
from SiphonServer.server.utils.logging_config import configure_logging
from SiphonServer.server.utils.exceptions import ServerError

## Services
from SiphonServer.server.services.get_status import get_status_service
from SiphonServer.server.services.chain_async import chain_async_service
from SiphonServer.server.services.chain_sync import chain_sync_service
from SiphonServer.server.services.generate_synthetic_data import generate_synthetic_data

# Response/request models
from Chain import ModelAsync, Prompt, Parser, Verbosity, ChainCache

# Setup logging
logger = configure_logging()

# Set up cache
dir_path = Path(__file__).parent
cached_path = dir_path / "server_cache.db"
ModelAsync._chain_cache = ChainCache(db_path=cached_path)

# Set up FastAPI app
app = FastAPI(
    title="Siphon & Chain API Server",
    description="Universal content ingestion and LLM processing API with GPU acceleration",
    version="1.0.0",
)

# Add at module level
startup_time = time.time()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from .... siphon
# Declare our FastAPI app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 SiphonServer starting up...")
    logger.info("🔥 GPU acceleration enabled for local models")
    yield
    # Shutdown
    logger.info("🛑 SiphonServer shutting down...")


# Status endpoint
@app.get("/status", response_model=StatusResponse)
async def get_status():
    return get_status_service(startup_time)


# Chain endpoints
@app.post("/chain/sync")
async def chain_sync(request: ChainRequest) -> ChainResponse | ChainError:
    return chain_sync_service(request)


@app.post("/chain/async")
async def chain_async(
    batch: BatchRequest,
) -> list[ChainResponse | ChainError]:
    return await chain_async_service(batch)


# Siphon endpoint
@app.post("/siphon/synthetic_data")
async def siphon_synthetic_data(request: SyntheticDataRequest):
    return generate_synthetic_data(request)


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "path": str(request.url)},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )


@app.exception_handler(ServerError)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.message, "code": exc.code}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="info")
