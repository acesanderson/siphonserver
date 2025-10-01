from conduit.sync import Model, Verbosity, ConduitCache
from siphonserver.server.api.requests import ConduitRequest
from siphonserver.server.api.responses import ConduitResponse, ConduitError
from siphonserver.server.utils.logging_config import get_logger
from pathlib import Path

# Set up cache
cache_file = Path(__file__).parent / ".server_cache.db"
Model._conduit_cache = ConduitCache(cache_file)  # Initialize cache if needed
# Set up logger
logger = get_logger(__name__)


def conduit_sync_service(request: ConduitRequest) -> ConduitResponse | ConduitError:
    """
    Synchronous Conduit processing function.
    Accepts ConduitRequest; returns ConduitResponse or ConduitError.
    """
    logger.info(f"Processing sync query for model: {request.model}")
    model = Model(request.model)
    response = model.query(request=request, verbose=Verbosity.SUMMARY)
    logger.info(f"Sync query completed for model: {request.model}")
    return response
