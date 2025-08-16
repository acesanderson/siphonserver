"""
Main orchestrator for the Siphon & Chain API server.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn

# Response/request models
from Chain import ModelAsync, Prompt, Parser, Verbosity, ChainCache
from app.api.requests import (
    ChainRequest,
    BatchRequest,
    SiphonSyntheticDataRequest,
)
from app.api.responses import (
    StatusResponse,
    ChainResponse,
    ChainError,
    SyntheticData,
)

# Utils
from app.utils.logging_config import configure_logging
from app.utils.exceptions import ServerError

# Services
from app.services.batch_runner import run_batch

# Setup logging
logger = configure_logging()

# Set up cache
dir_path = Path(__file__).parent
cached_path = dir_path / "server_cache.db"
ModelAsync._chain_cache = ChainCache(db_path=cached_path)

# Declare our FastAPI app
app = FastAPI(
    title="Siphon & Chain API Server",
    description="Universal content ingestion and LLM processing API with GPU acceleration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Health check endpoint"""
    try:
        # Test a simple model query to verify Chain is working
        test_model = Model("llama3.1:latest")  # Local Ollama model
        test_response = test_model.query("ping", verbose=Verbosity.SILENT)

        return StatusResponse(
            status="healthy",
            message="SiphonServer is running with Chain framework",
            models_available=Model.models(),
            gpu_enabled=True,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return StatusResponse(
            status="degraded",
            message=f"Issues detected: {str(e)}",
            models_available={},
            gpu_enabled=False,
        )


# Chain endpoints
@app.post("/chain/query")
async def chain_query(request: ChainQueryRequest) -> ChainResult:
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
) -> list[ChainResult]:
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
async def siphon_synthetic_data(request: SiphonSyntheticDataRequest):
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
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8080, reload=True, log_level="info"
    )
