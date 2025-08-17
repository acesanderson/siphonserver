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
from SiphonServer.server.services.async_chain import run_batch_query
from SiphonServer.server.services.sync_chain import run_sync_query

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
    try:
        from Chain import Model, Response, Verbosity
        import torch

        # Is ollama working?
        try:
            test_model = Model("llama3.1:latest")  # Local Ollama model
            test_response = test_model.query("ping", verbose=Verbosity.SILENT)
            if isinstance(test_response, Response):
                ollama_working = True
            else:
                raise ValueError(f"Invalid response from Ollama model: {test_response}")

        except Exception as e:
            ollama_working = False

        # Is CUDA available?
        gpu_enabled = torch.cuda.is_available() if torch else False

        # Get available models
        models_available = Model.models()["ollama"] if ollama_working else {}

        # What's the status?
        status = "healthy" if ollama_working and gpu_enabled else "degraded"

        # Uptime
        # In your status endpoint, replace the uptime line:
        uptime = time.time() - startup_time

        return StatusResponse(
            status=status,
            gpu_enabled=gpu_enabled,
            message="Server is running",
            models_available=models_available,
            uptime=uptime,
        )
    except Exception as e:
        return StatusResponse(
            status="error",
            gpu_enabled=False,
            message=f"Error retrieving status: {str(e)}",
            models_available={},
            uptime=None,
        )


# Chain endpoints
@app.post("/chain/query")
async def chain_query(request: ChainRequest) -> ChainResponse | ChainError:
    """
    Synchronous Chain query endpoint.
    Takes a ChainRequest and returns a ChainResponse OR ChainError.
    """
    try:
        logger.info(f"Processing sync query for model: {request.model}")

        # Create model instance
        model = Model(request.model)

        # Create Chain request
        chain_request = ChainRequest.from_query_input(
            query_input=request.query_input,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_model=request.response_model,
        )

        # Execute query
        result = model.query(
            request=chain_request, verbose=request.verbose, cache=request.cache
        )

        logger.info(f"Sync query completed for model: {request.model}")
        return result

    except Exception as e:
        logger.error(f"Sync query failed: {e}")
        return ChainError.from_exception(e, code="sync_query_error", category="server")


@app.post("/chain/async")
async def chain_async(
    batch: BatchRequest,
) -> list[ChainResponse | ChainError]:
    """
    Asynchronous batch Chain processing endpoint.
    Accepts BatchRequest; returns a list of ChainResponse or ChainError.
    """

    try:
        logger.info(
            f"Processing async batch with {len(batch.prompt_strings or batch.input_variables_list)} requests"
        )

        # Create async model
        model = ModelAsync(model=batch.model)

        # Optional prompt for template rendering
        prompt: Prompt | None = None
        if batch.input_variables_list and hasattr(batch, "prompt_template"):
            prompt = Prompt(batch.prompt_template)

        # Optional parser for structured responses
        parser: Parser | None = None
        if batch.response_model:
            parser = Parser(batch.response_model)

        # Execute batch
        results = await run_batch(
            model,
            batch,
            prompt=prompt,
            parser=parser,
            max_concurrency=max_concurrency,
            cache=cache,
            verbose=Verbosity.PROGRESS,
        )

        logger.info(f"Async batch completed with {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Async batch failed: {e}")
        # Return single error for the entire batch
        return [
            ChainError.from_exception(e, code="async_batch_error", category="server")
        ]


# Siphon endpoint
@app.post("/siphon/synthetic_data")
async def siphon_synthetic_data(request: SyntheticDataRequest):
    """
    Generate AI enrichments (titles, summaries, descriptions).
    Takes a SyntheticDataRequest and returns SyntheticData.
    """
    pass


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
