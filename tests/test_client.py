from siphonserver.server.api.requests import (
    ConduitRequest,
    SyntheticDataRequest,
    EmbeddingsRequest,
)
from siphonserver.client.siphonclient import SiphonClient
from siphonserver.server.utils.logging_config import configure_logging
import json
import requests
from pathlib import Path

logger = configure_logging()
client = SiphonClient()


def test_status():
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


def test_query_sync():
    logger.info("Sending synchronous query...")
    try:
        request = ConduitRequest.from_query_input(
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


def test_query_async_prompt_strings():
    from siphonserver.server.api.requests import BatchRequest
    from conduit.message.textmessage import TextMessage

    prompt_strings = [
        "What is the capital of France?",
        "Explain the theory of relativity.",
        "What are the benefits of meditation?",
    ]
    message = TextMessage(role="user", content="Please answer the following questions:")
    model = "gpt-oss:latest"
    request = BatchRequest(
        messages=[message],
        model=model,
        prompt_strings=prompt_strings,
    )
    logger.info("Sending asynchronous query...")
    try:
        results = client.query_async(request)
        print(results)
        logger.info("Asynchronous query sent successfully.")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")


def test_generate_synthetic_data():
    """
    Test the generation of synthetic data using a sample file.
    """
    logger.info("Generating synthetic data...")
    from siphon.data.uri import URI
    from siphon.data.context import Context

    sample_file = Path(__file__).parent / "sample.txt"
    uri = URI.from_source(sample_file)
    context = Context.from_uri(uri)
    request = SyntheticDataRequest(
        model="gpt-oss:latest",
        context=context,
    )
    try:
        synthetic_data = client.generate_synthetic_data(request)
        print(json.dumps(synthetic_data.model_dump(), indent=2))
        logger.info("Synthetic data generated successfully.")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")


def test_generate_embeddings():
    logger.info("Generating embeddings...")
    from conduit.embeddings.chroma_batch import ChromaBatch

    model = "sentence-transformers/all-MiniLM-L6-v2"
    batch = ChromaBatch(
        ids=["1", "2"],
        documents=["This is a test document.", "This is another test document."],
        metadatas=[{}, {}],
    )

    request = Embeddi_ngsRequest(
        model=model,
        batch=batch,
    )

    try:
        response = client.generate_embeddings(request)
        print(json.dumps(response.model_dump(), indent=2))
        logger.info("Embeddings generated successfully.")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")


def test_curator():
    logger.info("Testing curator service...")
    from siphonserver.server.api.requests import CuratorRequest

    params = {
        "query_string": "machine learning applications",
        "k": 3,
        "n_items": 5,
        "model": "bge",
        "cached": True,
    }
    request = CuratorRequest(**params)
    try:
        response = client.curate(request)
        print(json.dumps(response.model_dump(), indent=2))
        logger.info("Curator service tested successfully.")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"HTTP Error: {e}")
    except Exception as e:
        logger.warning(f"Error: {e}")
