from siphonserver.client.siphonclient import SiphonClient, EmbeddingsRequest
from conduit.embeddings.chroma_batch import ChromaBatch

sc = SiphonClient()
model = "sentence-transformers/all-mpnet-base-v2"
batch = ChromaBatch(
    ids=["1", "2"],
    documents=["This is a test document.", "This is another test document."],
    metadatas=[{}, {}],
)
request = EmbeddingsRequest(model=model, batch=batch)
embedded_batch = sc.generate_embeddings(request)
print(embedded_batch.model_dump_json(indent=2))
