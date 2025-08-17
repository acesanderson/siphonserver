from Chain import Model, Verbosity, ChainCache
from SiphonServer.server.api.requests import ChainRequest
from SiphonServer.server.api.responses import ChainResponse, ChainError
from SiphonServer.server.utils.logging_config import get_logger
from pathlib import Path

# Set up cache
cache_file = Path(__file__).parent / ".server_cache.db"
Model._chain_cache = ChainCache(cache_file)  # Initialize cache if needed
# Set up logger
logger = get_logger(__name__)


def run_sync_query(request: ChainRequest) -> ChainResponse | ChainError:
    """
    Synchronous Chain processing function.
    Accepts ChainRequest; returns ChainResponse or ChainError.
    """
    logger.info(f"Processing sync query for model: {request.model}")
    model = Model(request.model)
    response = model.query(request=request, verbose=Verbosity.SUMMARY)
    logger.info(f"Sync query completed for model: {request.model}")
    return response
