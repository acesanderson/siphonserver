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
from SiphonServer.server.utils.exceptions import SiphonServerError
import requests
import json

logger = configure_logging()


class SiphonServerException(Exception):
    """Client-side exception wrapping SiphonServerError"""

    def __init__(self, server_error: SiphonServerError):
        self.server_error = server_error
        super().__init__(server_error.message)

    def __str__(self):
        return (
            f"SiphonServer {self.server_error.error_type}: {self.server_error.message}"
        )


class SiphonClient:
    def __init__(self, base_url: str = ""):
        if base_url == "":
            self.base_url = self._get_url()
        else:
            self.base_url = base_url.rstrip("/")

    def _get_url(self) -> str:
        """Get SiphonServer URL with same host detection logic as PostgreSQL"""
        endpoints = [
            "http://localhost:8080",
            "http://10.0.0.87:8080",
            "http://68.47.92.102:8080",
        ]

        for url in endpoints:
            try:
                response = requests.get(f"{url}/status", timeout=1)
                if response.status_code == 200:
                    return url
            except:
                continue

        raise ConnectionError("Cannot reach SiphonServer on any known endpoint")

    def _handle_error_response(self, response: requests.Response) -> None:
        """Parse SiphonServerError from response and raise appropriate exception"""
        try:
            error_data = response.json()

            # Check if it's our structured error format
            if isinstance(error_data, dict) and "error_type" in error_data:
                server_error = SiphonServerError.model_validate(error_data)

                logger.error(
                    f"Server error [{server_error.request_id}]: {server_error.error_type}"
                )
                logger.error(f"Message: {server_error.message}")

                if server_error.validation_errors:
                    logger.error(
                        f"Validation errors: {json.dumps(server_error.validation_errors, indent=2)}"
                    )

                if server_error.context:
                    logger.error(
                        f"Context: {json.dumps(server_error.context, indent=2)}"
                    )

                raise SiphonServerException(server_error)

            # Fallback for non-structured errors
            logger.error(
                f"Non-structured error response: {json.dumps(error_data, indent=2)}"
            )

        except (json.JSONDecodeError, ValueError):
            # Raw text response
            logger.error(f"Raw error response: {response.text}")

        # Still raise the original HTTP error
        response.raise_for_status()

    def get_status(self):
        """Get server status"""
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def query_sync(self, request: ChainRequest) -> ChainResponse | ChainError:
        """Send a synchronous query to the server"""
        response = requests.post(
            f"{self.base_url}/chain/sync", json=request.model_dump()
        )
        response.raise_for_status()
        try:
            return ChainResponse.model_validate_json(response.text)
        except Exception as e:
            return ChainError.model_validate_json(response.text)

    def query_async(self, batch: BatchRequest) -> list[ChainResponse | ChainError]:
        """Send an asynchronous batch query to the server"""
        response = requests.post(
            f"{self.base_url}/chain/async", json=batch.model_dump()
        )
        response.raise_for_status()
        try:
            return [ChainResponse.model_validate_json(item) for item in response.json()]
        except Exception as e:
            return [ChainError.model_validate_json(item) for item in response.json()]

    def generate_synthetic_data(self, request) -> SyntheticData | ChainError:
        """Generate synthetic data using the server with structured error handling"""
        endpoint = f"{self.base_url}/siphon/synthetic_data"

        # Log the request details
        request_data = request.model_dump()
        logger.info(f"Sending request to {endpoint}")
        logger.debug(f"Request payload keys: {list(request_data.keys())}")
        logger.debug(f"Context type: {type(request.context).__name__}")
        logger.debug(f"Model: {request.model}")

        # Log a hash of the request for duplicate detection
        import hashlib

        request_hash = hashlib.md5(
            json.dumps(request_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        logger.info(f"Request hash: {request_hash}")

        try:
            response = requests.post(endpoint, json=request_data)

            # Log response details before checking status
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")

            # Extract request ID from response headers if available
            request_id = response.headers.get("X-Request-ID", "unknown")
            logger.info(f"Server request ID: {request_id}")

            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code} error from {endpoint}")
                self._handle_error_response(response)

            result = SyntheticData.model_validate_json(response.text)
            logger.info(f"Successfully received synthetic data [hash: {request_hash}]")
            return result

        except SiphonServerException:
            # Re-raise our structured exceptions
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTPError: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise
