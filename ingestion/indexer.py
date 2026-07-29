import pickle
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from rank_bm25 import BM25Okapi

from config.settings import (
    QDRANT_PATH,
    QDRANT_LOGS_COLLECTION,
    EMBEDDING_DIM,
    BM25_INDEX_PATH
)
from ingestion.embedder import get_embedder


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)


def setup_collection(client: QdrantClient, collection_name: str):
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"Created Qdrant collection: {collection_name}")
    else:
        print(f"Collection already exists: {collection_name}")


def store_in_qdrant(chunks, collection_name, client):
    embedder = get_embedder()
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedder,
    )
    vectorstore.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks in Qdrant [{collection_name}]")
    return vectorstore


def load_qdrant(collection_name: str):
    client = get_qdrant_client()
    embedder = get_embedder()
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedder,
    )


def build_bm25_index(chunks):
    tokenized = [doc.page_content.lower().split() for doc in chunks]
    bm25 = BM25Okapi(tokenized)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "documents": chunks}, f)
    print(f"BM25 index built and saved")
    return bm25, chunks


def load_bm25_index():
    with open(BM25_INDEX_PATH, "rb") as f:
        data = pickle.load(f)
    print(f"BM25 index loaded — {len(data['documents'])} documents")
    return data["bm25"], data["documents"]


def run_ingestion(chunks):
    print("\nStarting ingestion pipeline...")
    client = get_qdrant_client()
    setup_collection(client, QDRANT_LOGS_COLLECTION)
    store_in_qdrant(chunks, QDRANT_LOGS_COLLECTION, client)
    build_bm25_index(chunks)
    print(f"\nIngestion complete!")
    print(f"   {len(chunks)} chunks in Qdrant (dense)")
    print(f"   BM25 index saved (sparse)")
    print(f"   Ready for hybrid search")

