import time
import numpy as np


def cosine_similarity(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator else 0.0


def local_similarity(collection, query_vector, limit=3, source_tag=None):
    query = {"embedding": {"$exists": True}}
    if source_tag:
        query["source_tag"] = source_tag
    rows = []
    for doc in collection.find(query):
        rows.append({
            "tx_id": doc.get("tx_id"),
            "fraud_confirmed": doc.get("fraud_confirmed"),
            "fraud_type": doc.get("fraud_type"),
            "fraud_signature_text": doc.get("fraud_signature_text"),
            "score": round(cosine_similarity(query_vector, doc["embedding"]), 6),
            "search_mode": "local_fallback",
        })
    return sorted(rows, key=lambda x: x["score"], reverse=True)[:limit]


def search_frauds(collection, query_vector, index_name="fraud_vector_index", path="embedding", limit=3, num_candidates=50, source_tag=None, allow_fallback=True):
    started = time.perf_counter()
    pipeline = [
        {"$vectorSearch": {
            "index": index_name,
            "path": path,
            "queryVector": query_vector,
            "numCandidates": max(num_candidates, limit),
            "limit": limit,
        }},
        {"$project": {
            "_id": 0,
            "tx_id": 1,
            "fraud_confirmed": 1,
            "fraud_type": 1,
            "fraud_signature_text": 1,
            "score": {"$meta": "vectorSearchScore"},
        }},
    ]
    try:
        rows = list(collection.aggregate(pipeline))
        for row in rows:
            row["search_mode"] = "atlas_vector_search"
        return {
            "results": rows,
            "mode": "atlas_vector_search",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": None,
        }
    except Exception as exc:
        if not allow_fallback:
            raise
        rows = local_similarity(collection, query_vector, limit, source_tag)
        return {
            "results": rows,
            "mode": "local_fallback",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": str(exc),
        }
