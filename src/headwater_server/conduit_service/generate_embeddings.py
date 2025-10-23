from headwater_api.classes import EmbeddingsRequest, EmbeddingsResponse

import logging

logger = logging.getLogger(__name__)


async def generate_embeddings_service(
    request: EmbeddingsRequest,
) -> EmbeddingsResponse:
    """
    Generate embeddings for a batch of documents based on the provided request.
    This function simulates the generation of embeddings using a specified model.
    """
    from conduit.embeddings.embedding_model import EmbeddingModel
    from conduit.embeddings.chroma_batch import ChromaBatch

    model: str = request.model
    batch: ChromaBatch = request.batch

    logger.info(f"Generating embeddings using model: {model}")

    if batch.embeddings:
        raise ValueError("Embeddings already exist in the provided batch.")

    embedding_model = EmbeddingModel(model)
    new_batch: ChromaBatch = embedding_model.generate_embeddings(batch)
    response = EmbeddingsResponse(embeddings=new_batch.embeddings)
    return response
