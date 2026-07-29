import pickle
from config.settings import BM25_INDEX_PATH, SPARSE_TOP_K


def sparse_search(query: str, k: int = SPARSE_TOP_K) -> list:
    """
    BM25 keyword search.
    Best for: exact terms
    e.g. "bench press", "chest day", "65kg"
    """
    with open(BM25_INDEX_PATH, "rb") as f:
        data = pickle.load(f)

    bm25 = data["bm25"]
    documents = data["documents"]

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    # Get top-k indices sorted by score
    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    # Return list of (Document, score) tuples
    results = [
        (documents[i], float(scores[i]))
        for i in top_indices
        if scores[i] > 0  # only return docs with non-zero score
    ]

    return results
