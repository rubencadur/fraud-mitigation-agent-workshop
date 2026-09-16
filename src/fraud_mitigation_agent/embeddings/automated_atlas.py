"""Optional path: let Atlas compute embeddings server-side (Automated Embeddings).

Unlike embeddings/manual.py, this never runs locally — Atlas calls a hosted
embedding model (e.g. voyage-4) itself, both when indexing documents and when
running a text-based $vectorSearch query. Availability depends on Atlas
region/tier/preview status, so the manual path remains the required baseline.
"""


def auto_embedding_index_definition(path="fraud_signature_text", model="voyage-4"):
    """Return the Atlas Vector Search Automated Embedding definition."""
    return {
        "fields": [
            {
                "type": "autoEmbed",
                "path": path,
                "model": model,
                "modality": "text",
            }
        ]
    }


def create_auto_embedding_index(collection, name="fraud_auto_embedding_index", path="fraud_signature_text", model="voyage-4"):
    definition = auto_embedding_index_definition(path=path, model=model)
    return collection.create_search_index({
        "name": name,
        "type": "vectorSearch",
        "definition": definition,
    })


def automated_text_search(collection, query_text, index_name="fraud_auto_embedding_index", path="fraud_signature_text", limit=3):
    # Note query.text instead of a queryVector: Atlas embeds query_text
    # server-side using the model configured on the index, so the caller
    # never has to generate or send a vector itself.
    pipeline = [
        {"$vectorSearch": {
            "index": index_name,
            "query": {"text": query_text},
            "path": path,
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
    return list(collection.aggregate(pipeline))
