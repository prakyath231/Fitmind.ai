from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_logs(documents: list[Document]) -> list[Document]:
    """
    For daily logs — each entry stays as ONE chunk.
    Daily logs are already the right size (200-400 tokens).
    We only split if an entry is extremely long.

    Why we DON'T split aggressively here:
    - Each day entry needs to stay together for context
    - "Bench Press 60kg + skipped dinner" must be one chunk
    - Splitting would break the day's story
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunked = splitter.split_documents(documents)

    # Preserve metadata through chunking
    # (LangChain does this automatically)

    print(f"✅ Chunked into {len(chunked)} chunks")
    return chunked
