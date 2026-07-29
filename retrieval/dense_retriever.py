from langchain_qdrant import QdrantVectorStore
from config.settings import QDRANT_LOGS_COLLECTION, DENSE_TOP_K
from ingestion.indexer import get_qdrant_client
from ingestion.embedder import get_embedder


def dense_search(query: str, k: int = DENSE_TOP_K) -> list:
    """
    Semantic search using Qdrant vector similarity.
    Best for: meaning-based queries
    e.g. "when did I feel tired after training"
    """
    client = get_qdrant_client()
    embedder = get_embedder()

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_LOGS_COLLECTION,
        embedding=embedder,
    )

    results = vectorstore.similarity_search_with_score(query, k=k)

    # results = list of (Document, score) tuples
    return results
