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
