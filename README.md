# SiphonServer

High-performance GPU-accelerated API server for distributed content processing and LLM operations. Built on Siphon's universal content ingestion and Chain's LLM orchestration.

## Architecture Problem

**Why SiphonServer exists:** While Siphon and Chain work excellently for local processing, certain workloads benefit from centralized GPU resources, async batch processing, and shared caching. SiphonServer addresses these specific use cases without replacing the core libraries.

## Core Value Propositions

### 1. GPU Acceleration Pool
Centralize expensive GPU resources for multiple clients:
```bash
# Client sends CPU-intensive work to GPU server
curl -X POST http://server:8080/siphon/synthetic_data \
  -d '{"context": {...}, "model": "llama3.3:latest"}'
```

### 2. Async Batch Processing
Process multiple requests concurrently:
```python
batch = BatchRequest(
    model="gpt-oss:latest",
    prompt_strings=[
        "Analyze this financial report...",
        "Summarize this research paper...",
        "Extract key points from..."
    ]
)
results = await client.query_async(batch)
```

### 3. Shared Caching Layer
Avoid duplicate processing across teams:
- ProcessedContent cached in PostgreSQL
- LLM responses cached via Chain
- Intelligent cache invalidation

## Quick Start

### Server Setup
```bash
# Install with GPU support
pip install -e .

# Configure environment
export POSTGRES_PASSWORD="your_password"
export OPENAI_API_KEY="your_key"  # Optional

# Start server
python server/main.py
# Server runs on http://localhost:8080
```

### Client Usage
```python
from SiphonServer.client import SiphonClient
from SiphonServer.server.api.requests import SyntheticDataRequest
from Siphon.data.URI import URI
from Siphon.data.Context import Context

client = SiphonClient()

# Process content remotely
uri = URI.from_source("quarterly-report.pdf")
context = Context.from_uri(uri)
request = SyntheticDataRequest(context=context, model="llama3.3:latest")

synthetic_data = client.generate_synthetic_data(request)
print(f"Title: {synthetic_data.title}")
print(f"Summary: {synthetic_data.summary}")
```

## API Endpoints

### Status & Health
```
GET /status
```
Returns server status, available models, GPU status, and uptime.

### Chain Processing
```
POST /chain/sync      # Single synchronous request
POST /chain/async     # Batch asynchronous processing
```

### Siphon Operations
```
POST /siphon/synthetic_data    # Generate titles, summaries, descriptions
```

## Relationship to Core Projects

### Siphon Integration
- **Input:** Uses Siphon's `Context` objects for universal content format
- **Output:** Returns Siphon's `SyntheticData` objects
- **Cache:** Leverages Siphon's PostgreSQL caching system

### Chain Integration  
- **Models:** All Chain-supported models available (Ollama, OpenAI, etc.)
- **Processing:** Chain's async capabilities for batch operations
- **Caching:** Chain's response caching prevents duplicate LLM calls

### When to Use SiphonServer vs. Direct Libraries

**Use SiphonServer when:**
- Processing large batches (>10 documents)
- Need GPU acceleration but lack local GPU
- Want shared caching across team/organization
- Building web applications that need async processing

**Use direct libraries when:**
- Single document processing
- Privacy-sensitive content (process locally)
- No network connectivity
- Simple automation scripts

## Performance Features

### GPU Acceleration
- Automatic GPU detection and utilization
- CUDA support for compatible models
- Graceful fallback to CPU processing

### Batch Optimization
```python
# Process 50 summaries in parallel
batch = BatchRequest(
    model="cogito:32b",
    prompt_strings=document_prompts  # List of 50 strings
)
results = await client.query_async(batch)  # ~10x faster than sequential
```

### Intelligent Caching
- Content-aware deduplication
- PostgreSQL full-text search
- Automatic cache warming for common operations

## Error Handling & Monitoring

### Structured Error Responses
```python
try:
    result = client.generate_synthetic_data(request)
except SiphonServerException as e:
    print(f"Server error: {e.server_error.error_type}")
    print(f"Message: {e.server_error.message}")
    print(f"Request ID: {e.server_error.request_id}")
```

### Observability
- Comprehensive request/response logging
- Performance metrics per model
- Cache hit/miss statistics
- GPU utilization tracking

## Production Deployment

### Docker Setup
```dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04
# ... GPU-enabled container setup
```

### Environment Configuration
```bash
# Required
POSTGRES_PASSWORD=your_secure_password

# Optional - enables cloud models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Performance tuning
MAX_BATCH_SIZE=50
WORKER_PROCESSES=4
GPU_MEMORY_FRACTION=0.8
```

### Security Considerations
- No data persistence beyond caching
- Request-scoped logging with IDs
- Configurable model access controls
- Network isolation for sensitive deployments

## Development & Evaluation

### Model Performance Testing
```bash
# Benchmark all available models
python eval/timing.py

# Generate evaluation dataset
python eval/candidate_summaries.py

# Run quality assessments
python eval/eval.py
```

### Custom Model Integration
Add new model providers by extending Chain's model system - SiphonServer automatically inherits new capabilities.

## Contributing

SiphonServer is designed as infrastructure - focus areas:

1. **Performance optimization** - Batch processing, GPU utilization
2. **Monitoring & observability** - Better metrics and alerting  
3. **Model support** - Integration with new LLM providers
4. **Deployment automation** - Kubernetes, Docker Compose setups

## License

MIT License - Same as Siphon and Chain

---

*Transform any content into structured knowledge at scale. GPU-accelerated processing for the agent future.*

**Ready to scale your knowledge pipeline?**

```bash
pip install -e .
python server/main.py
# Your team's content processing hub is ready
```
