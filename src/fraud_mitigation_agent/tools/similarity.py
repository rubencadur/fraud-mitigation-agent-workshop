from ._common import run_tool
from ..embeddings.manual import deterministic_embedding, text_for_transaction
from ..vector_search.queries import search_frauds


def find_similar_fraud(db, transaction: dict, signals=None, index_name="fraud_vector_index", dimensions=8, source_tag=None):
    def work():
        text = transaction.get("fraud_signature_text") or text_for_transaction(transaction, [s.get("code", "") for s in (signals or [])])
        vector = transaction.get("embedding") or deterministic_embedding(text, dimensions)
        result = search_frauds(db.fraud_patterns, vector, index_name=index_name, source_tag=source_tag)
        result["query_text"] = text
        return result
    return run_tool("find_similar_fraud", work)
