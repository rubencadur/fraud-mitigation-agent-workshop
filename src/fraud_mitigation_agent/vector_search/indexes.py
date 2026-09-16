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
