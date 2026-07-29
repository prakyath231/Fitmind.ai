from retrieval.dense_retriever import dense_search
from retrieval.sparse_retriever import sparse_search
from config.settings import DENSE_TOP_K, SPARSE_TOP_K, FINAL_TOP_K, RRF_K


def reciprocal_rank_fusion(
    dense_results: list,
    sparse_results: list,
    k: int = RRF_K
) -> list:
    """
    Combines dense and sparse results using RRF.

    RRF formula: score = 1 / (k + rank)
    A document ranked #1 in both lists wins.
    Scale-invariant — works across different score ranges.
    """
    scores = {}
    doc_map = {}

    # Score dense results
    for rank, (doc, _) in enumerate(dense_results):
        doc_id = doc.page_content[:100]  # use content as unique key
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        doc_map[doc_id] = doc

    # Score sparse results
    for rank, (doc, _) in enumerate(sparse_results):
        doc_id = doc.page_content[:100]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        doc_map[doc_id] = doc

    # Sort by combined RRF score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    return [
        (doc_map[doc_id], scores[doc_id])
        for doc_id in sorted_ids
    ]


def hybrid_search(query: str, k: int = FINAL_TOP_K) -> list:
    """
    Full hybrid search pipeline:
    1. Dense search (Qdrant semantic)
    2. Sparse search (BM25 keyword)
    3. Merge with RRF
    4. Return top-k

    This is what the agents call for every query.
    """
    print(f"\nHybrid search: '{query}'")

    # 1. Dense
    dense_results = dense_search(query, k=DENSE_TOP_K)
    print(f"  Dense results  : {len(dense_results)}")

    # 2. Sparse
    sparse_results = sparse_search(query, k=SPARSE_TOP_K)
    print(f"  Sparse results : {len(sparse_results)}")

    # 3. RRF merge
    merged = reciprocal_rank_fusion(dense_results, sparse_results)

    # 4. Top-k
    final = merged[:k]
    print(f"  Final results  : {len(final)} (after RRF)")

    return final


def format_context(results: list) -> str:
    """
    Formats retrieved chunks into a clean context string
    for the LLM prompt.
    """
    if not results:
        return "No relevant logs found."

    context_parts = []
    for i, (doc, score) in enumerate(results):
        context_parts.append(
            f"[Log {i+1} | RRF score: {score:.4f}]\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(context_parts)
