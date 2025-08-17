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
from SiphonServer.server.utils.logging_config import configure_logging
import requests
import json


logger = configure_logging()


class SiphonClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")

    def get_status(self):
        """Get server status"""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def query_sync(self, request: ChainRequest) -> ChainResponse | ChainError:
        """Send a synchronous query to the server"""
        response = requests.post(
            f"{self.base_url}/chain/query", json=request.model_dump()
        )
        response.raise_for_status()
        try:
            return ChainResponse.model_validate_json(response.text)
        except Exception as e:
            return ChainError.model_validate_json(response.text)


if __name__ == "__main__":
    client = SiphonClient()

    logger.info("Checking server status...")
    try:
        status = client.get_status()
        print(json.dumps(status, indent=2))
        logger.info("Server status retrieved successfully.")
    except requests.exceptions.ConnectionError:
        logger.warning("Error: Could not connect to server at http://localhost:8080")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")

    logger.info("Sending synchronous query...")
    try:
        request = ChainRequest.from_query_input(
            model="llama3.1:latest",
            query_input="Tell me a joke about llamas",
        )
        response = client.query_sync(request)
        print(json.dumps(response.model_dump(), indent=2))
        logger.info("Synchronous query sent successfully.")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")
