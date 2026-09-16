"""Atlas Vector Search index definitions for the manual embedding path.

`dimensions` must match the length of the vectors produced by
embeddings/manual.py's deterministic_embedding() (default 8) — an index
built for the wrong dimension count will simply reject queries.
"""


def vector_index_definition(path="embedding", dimensions=8, similarity="cosine"):
    return {
        "fields": [{
            "type": "vector",
            "path": path,
            "numDimensions": dimensions,
            "similarity": similarity,
        }]
    }


def create_vector_index(collection, name="fraud_vector_index", path="embedding", dimensions=8, similarity="cosine"):
    return collection.create_search_index({
        "name": name,
        "type": "vectorSearch",
        "definition": vector_index_definition(path, dimensions, similarity),
    })
