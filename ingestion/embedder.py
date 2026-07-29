from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL, EMBEDDING_DEVICE

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        print("Loading embedding model (first time ~30s)...")
        _embedder = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": True}
        )
        print(f"Embedding model loaded: {EMBEDDING_MODEL}")
    return _embedder
