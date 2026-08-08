import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from datetime import datetime
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from rank_bm25 import BM25Okapi
from ingestion.indexer import get_qdrant_client, setup_collection
from ingestion.embedder import get_embedder
from tools.log_extractor import format_log_entry
from config.settings import (
    QDRANT_LOGS_COLLECTION,
    BM25_INDEX_PATH,
)


def build_metadata(extracted: dict) -> dict:
    """Builds Qdrant metadata from extracted log data."""
    date_str = extracted.get("date", datetime.now().strftime("%Y-%m-%d"))
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        week = dt.strftime("%Y-W%W")
        day_of_week = dt.strftime("%A")
    except:
        week = "unknown"
        day_of_week = "unknown"

    macros = extracted.get("macros", {})
    muscles = extracted.get("muscles_trained", [])

    return {
        "source": "personal_log",
        "date": date_str,
        "week": week,
        "day_of_week": day_of_week,
        "type": extracted.get("type", "Workout"),
        "muscles_trained": muscles,
        "exercise_names": [e.get("name", "") for e in extracted.get("exercises", [])],
        "protein_g": macros.get("protein_g", 0),
        "calories": macros.get("calories", 0),
        "carbs_g": macros.get("carbs_g", 0),
        "fat_g": macros.get("fat_g", 0),
        "mood": extracted.get("mood", "average"),
        "is_rest_day": extracted.get("type", "").lower() == "rest day",
    }


def auto_ingest_log(extracted: dict) -> bool:
    """
    Takes extracted log data and ingests it into:
    1. Qdrant (dense vectors)
    2. BM25 index (sparse)
    3. Appends to daily_logs.txt

    Returns True if successful.
    """
    try:
        # Format log entry text
        log_text = format_log_entry(extracted)
        metadata = build_metadata(extracted)

        # Create document
        doc = Document(page_content=log_text, metadata=metadata)

        # 1. Ingest into Qdrant
        client = get_qdrant_client()
        setup_collection(client, QDRANT_LOGS_COLLECTION)
        embedder = get_embedder()

        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=QDRANT_LOGS_COLLECTION,
            embedding=embedder,
        )
        vectorstore.add_documents([doc])
        print(f"Ingested into Qdrant: {metadata['date']}")

        # 2. Update BM25 index
        try:
            with open(BM25_INDEX_PATH, "rb") as f:
                data = pickle.load(f)
            existing_docs = data["documents"]
        except FileNotFoundError:
            existing_docs = []

        all_docs = existing_docs + [doc]
        tokenized = [d.page_content.lower().split() for d in all_docs]
        bm25 = BM25Okapi(tokenized)

        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump({"bm25": bm25, "documents": all_docs}, f)
        print(f"Updated BM25 index: {len(all_docs)} total docs")

        # 3. Append to daily_logs.txt
        log_path = "data/logs/daily_logs.txt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n{log_text}")
        print(f"Appended to daily_logs.txt")

        return True

    except Exception as e:
        print(f"Auto-ingest error: {e}")
        return False


def build_confirmation_message(extracted: dict) -> str:
    """
    Builds a friendly confirmation message to show the user
    after their log is saved.
    """
    parts = []
    date = extracted.get("date", "today")
    entry_type = extracted.get("type", "Workout")

    parts.append(f"Logged for {date}")

    exercises = extracted.get("exercises", [])
    if exercises:
        ex_names = [e.get("name", "") for e in exercises]
        parts.append(f"Exercises: {', '.join(ex_names)}")

    macros = extracted.get("macros", {})
    if macros.get("protein_g"):
        parts.append(f"Protein: {macros['protein_g']}g")
    if macros.get("calories"):
        parts.append(f"Calories: {macros['calories']} kcal")

    muscles = extracted.get("muscles_trained", [])
    if muscles:
        parts.append(f"Muscles: {', '.join(muscles)}")

    return "\n".join(parts)
