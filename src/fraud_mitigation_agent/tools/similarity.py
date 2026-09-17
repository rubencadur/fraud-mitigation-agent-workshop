"""Tool: compare this transaction's embedding against known fraud patterns.

`deterministic_embedding`, `text_for_transaction` and `search_frauds` are
plain helper functions (not Tools themselves) that this one Tool uses
internally.
"""
from langchain_core.tools import tool
from ..embeddings.manual import deterministic_embedding, text_for_transaction
from ..vector_search.queries import search_frauds


def make_find_similar_fraud_tool(db, index_name="fraud_vector_index", dimensions=8, source_tag=None):
    @tool
    def find_similar_fraud(transaction: dict, signal_codes: list) -> dict:
        """Compare this transaction's embedding against known fraud patterns."""
        # Prefer a precomputed embedding/signature (set by synthetic.py fixtures);
        # otherwise build one on the fly from the transaction + behavioral signals.
        text = transaction.get("fraud_signature_text") or text_for_transaction(transaction, signal_codes)
        vector = transaction.get("embedding") or deterministic_embedding(text, dimensions)
        result = search_frauds(db.fraud_patterns, vector, index_name=index_name, source_tag=source_tag)
        result["query_text"] = text
        return result

    return find_similar_fraud
