"""
Main orchestrator for the Headwater Server.
"""

# FastAPI related imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from pydantic import ValidationError
import uvicorn
import time
import json

# Project Imports
## Models
from headwater_api.classes import (
    ConduitRequest,
    BatchRequest,
    SyntheticDataRequest,
    EmbeddingsRequest,
    CuratorRequest,
    StatusResponse,
    ConduitResponse,
    BatchResponse,
    ConduitError,
    EmbeddingsResponse,
    CuratorResponse,
    HeadwaterServerError,
    ErrorType,
)


## Services
from headwater_server.conduit_service.conduit_async_service import conduit_async_service
from headwater_server.conduit_service.conduit_sync_service import conduit_sync_service
from headwater_server.embeddings_service.embeddings_service import (
    generate_embeddings_service,
)
from headwater_server.curator_service.curator_service import curator_service
from headwater_server.status_service.get_status import get_status_service
# from headwater_server.siphon_service.generate_synthetic_data import (
#     generate_synthetic_data,
# )

from conduit.batch import ModelAsync, ConduitCache
import logging
import os

# Set up logging and cache
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "2"))  # Default to INFO
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO), format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
ModelAsync.conduit_cache = ConduitCache(name="headwater")

# Record up time
startup_time = time.time()


# Configure server
## Set up lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Headwater Server starting up...")
    logger.info("🔥 GPU acceleration enabled for local models")
    from conduit.sync import Model

    _ = Model._odometer_registry  # Initialize to load models and GPU resource

    yield
    # Shutdown
    logger.info("🛑 Headwater Server shutting down...")


## Set up FastAPI app
app = FastAPI(
    title="Headwater API Server",
    description="Universal content ingestion and LLM processing API with GPU acceleration",
    version="1.0.0",
    lifespan=lifespan,
)

## Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints
## Status endpoint
@app.get("/status", response_model=StatusResponse)
async def get_status():
    return get_status_service(startup_time)


# Conduit endpoints
@app.post("/conduit/sync")
def conduit_sync(request: ConduitRequest) -> ConduitResponse | ConduitError:
    return conduit_sync_service(request)


@app.post("/conduit/async")
async def conduit_async(
    batch: BatchRequest,
) -> BatchResponse:
    return await conduit_async_service(batch)


@app.post("/conduit/embeddings")
async def generate_embeddings(request: EmbeddingsRequest) -> EmbeddingsResponse:
    """Generate synthetic data with structured error handling"""
    return await generate_embeddings_service(request)


## Siphon endpoint
# @app.post("/siphon/synthetic_data")
# async def siphon_synthetic_data(request: SyntheticDataRequest):
#     """Generate synthetic data with structured error handling"""
#     request_id = (
#         getattr(request.state, "request_id", "unknown")
#         if hasattr(request, "state")
#         else "unknown"
#     )
#
#     logger.info(f"[{request_id}] Received synthetic data request")
#     logger.debug(f"[{request_id}] Request model: {request.model}")
#     logger.debug(f"[{request_id}] Context type: {type(request.context).__name__}")
#     logger.debug(f"[{request_id}] Context sourcetype: {request.context.sourcetype}")
#
#     try:
#         # Log the context size to detect potential issues
#         context_length = (
#             len(request.context.context) if hasattr(request.context, "context") else 0
#         )
#         logger.debug(f"[{request_id}] Context length: {context_length} characters")
#
#         # Call the service
#         result = await generate_synthetic_data(request)
#
#         logger.info(f"[{request_id}] Successfully generated synthetic data")
#         logger.debug(
#             f"[{request_id}] Generated title: {result.title[:50]}..."
#             if result.title
#             else "No title"
#         )
#         logger.info(result)
#
#         return result
#
#     except ValidationError as e:
#         logger.error(f"[{request_id}] Validation error in synthetic data generation")
#
#         # Create structured error
#         error = (
#             HeadwaterServerError(
#                 error_type=ErrorType.DATA_VALIDATION,
#                 message="Synthetic data validation failed",
#                 status_code=422,
#                 request_id=request_id,
#                 validation_errors=e.errors(),
#                 original_exception=str(e),
#             )
#             .add_context("context_type", type(request.context).__name__)
#             .add_context("model", request.model)
#         )
#
#         logger.error(f"[{request_id}] Error details: {error.model_dump_json()}")
#
#         raise HTTPException(status_code=422, detail=error.model_dump())
#
#     except Exception as e:
#         logger.error(f"[{request_id}] Unexpected error: {type(e).__name__}: {str(e)}")
#
#         # Create structured error
#         error = (
#             HeadwaterServerError.from_general_exception(
#                 e, status_code=500, include_traceback=True
#             )
#             .add_context("request_id", request_id)
#             .add_context("context_type", type(request.context).__name__)
#             .add_context("model", request.model)
#         )
#
#         logger.error(f"[{request_id}] Full error details: {error.model_dump_json()}")
#
#         raise HTTPException(status_code=500, detail=error.model_dump())


@app.post("/curator/curate")
async def curate(request: CuratorRequest) -> CuratorResponse:
    """Curate items based on the provided request"""
    return await curator_service(request)


# Error handlers
@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: HTTPException):
    """Enhanced 422 handler using HeadwaterServerError"""

    # Log request details for debugging
    try:
        body = await request.body()
        if body:
            try:
                json_body = json.loads(body)
                logger.error(f"Request body: {json.dumps(json_body, indent=2)}")
            except:
                logger.error(f"Request body (raw): {body[:500]}...")
    except Exception as e:
        logger.error(f"Could not read request body: {e}")

    # Create structured error response
    error = HeadwaterServerError(
        error_type=ErrorType.VALIDATION_ERROR,
        message="Request validation failed",
        status_code=422,
        path=str(request.url.path),
        method=request.method,
        request_id=getattr(request.state, "request_id", None),
        original_exception=str(getattr(exc, "detail", "No details available")),
    ).add_context("headers", dict(request.headers))

    logger.error(f"Validation error: {error.model_dump_json()}")

    return JSONResponse(status_code=422, content=error.model_dump())


@app.exception_handler(RequestValidationError)
async def pydantic_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    """Handle Pydantic validation errors with HeadwaterServerError"""

    error = HeadwaterServerError.from_validation_error(
        exc, request, include_traceback=False
    ).add_context("error_count", len(exc.errors()))

    logger.error(f"Pydantic validation error: {error.model_dump_json()}")

    return JSONResponse(status_code=422, content=error.model_dump())


@app.exception_handler(ValidationError)
async def general_validation_error_handler(request: Request, exc: ValidationError):
    """Handle general Pydantic ValidationErrors"""

    error = HeadwaterServerError.from_validation_error(
        exc, request, include_traceback=True
    )
    error.error_type = ErrorType.DATA_VALIDATION

    logger.error(f"General validation error: {error.model_dump_json()}")

    return JSONResponse(status_code=422, content=error.model_dump())


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""

    error = HeadwaterServerError.from_general_exception(
        exc, request, status_code=500, include_traceback=True
    )

    logger.error(f"Unhandled exception: {error.model_dump_json()}")

    return JSONResponse(status_code=500, content=error.model_dump())


def main():
    """Run the Uvicorn server"""
    from headwater_server.server.logo import print_logo

    watch_directory = str(Path(__file__).parent.parent.parent)

    print_logo()

    uvicorn.run(
        "headwater_server.server.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=[watch_directory],
        log_level="info",
    )


if __name__ == "__main__":
    main()
