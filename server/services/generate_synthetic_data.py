# In server/services/generate_synthetic_data.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from SiphonServer.server.api.requests import SyntheticDataRequest
from Siphon.data.SyntheticData import SyntheticData


async def generate_synthetic_data(
    request: SyntheticDataRequest,
) -> SyntheticData:
    """
    Generate synthetic data based on the provided request.
    This function simulates the generation of synthetic data such as titles, summaries, and descriptions.
    """
    context = request.context
    model = request.model
    server_side = True

    # Run your existing sync function in a thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        synthetic_data = await loop.run_in_executor(
            executor,
            SyntheticData.from_context,  # Your existing sync function
            context,  # context argument
            False,  # local argument
            model,  # model_str argument
            server_side,  # server_side argument
        )

    return synthetic_data
