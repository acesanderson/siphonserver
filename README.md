# SiphonServer

## Project Purpose

SiphonServer is a FastAPI-based server that provides unified HTTP endpoints for LLM processing and synthetic data generation. It wraps two core libraries—Conduit (for LLM chain orchestration) and Siphon (for content ingestion)—exposing both synchronous and asynchronous query endpoints along with GPU-accelerated local model execution. The server handles request validation, error formatting, and caching while providing a client library for programmatic access.

## Architecture Overview

- **server.main**: FastAPI application orchestrator with lifecycle management, CORS middleware, and centralized exception handlers
- **server.services.conduit_sync**: Synchronous LLM query processing using Conduit's Model interface
- **server.services.conduit_async**: Asynchronous batch query processing with thread pool execution for non-blocking operations
- **server.services.generate_synthetic_data**: Async wrapper around Siphon's synthetic data generation from context objects
- **server.services.get_status**: Health check service reporting model availability, GPU status, and uptime
- **server.api.requests**: Request models including ConduitRequest, BatchRequest, and SyntheticDataRequest with validation
- **server.api.responses**: Response models wrapping Conduit results, errors, and server status
- **server.utils.exceptions**: Structured error handling with SiphonServerError and ErrorType enumeration
- **server.utils.logging_config**: Centralized logging configuration with per-module logger management
- **client.siphonclient**: Python client library providing typed HTTP methods and automatic error deserialization
- **eval**: Model evaluation suite for comparing LLM outputs against gold standards across multiple dimensions

## Dependencies

**Major Dependencies:**
- `fastapi`: Web framework for API server
- `uvicorn`: ASGI server for FastAPI
- `pydantic`: Data validation and serialization
- `requests`: HTTP client library
- `torch`: PyTorch for GPU detection and acceleration
- `pandas`: Data analysis for evaluation module

**Local/Internal Dependencies:**
- `conduit`: LLM chain orchestration library (sync/async models, prompts, parsers, caching)
- `siphon`: Content ingestion and synthetic data generation library
- `dbclients`: Database client utilities providing network context

## API Documentation

### SiphonClient

**`__init__(base_url: str = "")`**
Initialize client with optional custom base URL. Defaults to network context configuration.

**`get_status() -> dict`**
Retrieve server health status including available models, GPU state, and uptime.

**`query_sync(request: ConduitRequest) -> ConduitResponse | ConduitError`**
Execute synchronous LLM query. Returns structured response or error object.

**`query_async(batch: BatchRequest) -> list[ConduitResponse | ConduitError]`**
Execute asynchronous batch queries with multiple prompts or input variable sets.

**`generate_synthetic_data(request: SyntheticDataRequest) -> SyntheticDataUnion | ConduitError`**
Generate synthetic data (title, summary, descriptions) from context object using specified model.

### Server Endpoints

**`GET /status`**
Returns StatusResponse with server health, model availability, GPU status, and uptime.

**`POST /conduit/sync`**
Accepts ConduitRequest, returns ConduitResponse or ConduitError for single LLM query.

**`POST /conduit/async`**
Accepts BatchRequest with multiple prompts or input variables, returns list of results.

**`POST /siphon/synthetic_data`**
Accepts SyntheticDataRequest with context object, returns SyntheticData subclass matching source type.

### Request Models

**`ConduitRequest`**
- `model: str` - Model identifier (e.g., "llama3.1:latest", "gpt-oss:latest")
- `prompt_str: str` - Template string or direct prompt
- `input_variables: dict[str, str]` - Variables for template rendering

**`BatchRequest(ConduitRequest)`**
- `prompt_strings: list[str]` - Multiple fully-rendered prompts
- `input_variables_list: list[dict[str, str]]` - Multiple variable sets for single template
- Validates exactly one of prompt_strings or input_variables_list is provided

**`SyntheticDataRequest`**
- `context: ContextUnion` - Siphon context object (file, URL, database record)
- `model: str` - Model to use for generation (default: "gemini2.5")

### Error Handling

**`SiphonServerError`**
Structured error model with:
- `error_type: ErrorType` - Enumerated error category
- `message: str` - Human-readable description
- `status_code: int` - HTTP status code
- `validation_errors: list[dict]` - Pydantic validation details
- `context: dict` - Additional debugging information
- `traceback: str` - Optional stack trace

**`SiphonServerException`**
Client-side exception wrapping SiphonServerError for local error handling.

## Usage Examples

### Basic Synchronous Query

```python
from siphonserver.client.siphonclient import SiphonClient
from siphonserver.server.api.requests import ConduitRequest

client = SiphonClient()

# Create request
request = ConduitRequest.from_query_input(
    model="llama3.1:latest",
    query_input="Explain quantum entanglement in simple terms"
)

# Execute query
response = client.query_sync(request)
print(response.content)
```

### Async Batch Processing

```python
from siphonserver.client.siphonclient import SiphonClient
from siphonserver.server.api.requests import BatchRequest

client = SiphonClient()

# Multiple independent prompts
batch = BatchRequest(
    model="gpt-oss:latest",
    prompt_strings=[
        "What is photosynthesis?",
        "Explain machine learning.",
        "Describe the water cycle."
    ]
)

results = client.query_async(batch)
for result in results:
    if isinstance(result, ConduitResponse):
        print(result.content)
```

### Synthetic Data Generation

```python
from siphonserver.client.siphonclient import SiphonClient
from siphonserver.server.api.requests import SyntheticDataRequest
from siphon.data.URI import URI
from siphon.data.Context import Context
from pathlib import Path

client = SiphonClient()

# Create context from file
uri = URI.from_source(Path("document.pdf"))
context = Context.from_uri(uri)

# Generate synthetic data
request = SyntheticDataRequest(
    context=context,
    model="gemini2.5"
)

synthetic_data = client.generate_synthetic_data(request)
print(f"Title: {synthetic_data.title}")
print(f"Summary: {synthetic_data.summary}")
print(f"Description: {synthetic_data.description}")
```