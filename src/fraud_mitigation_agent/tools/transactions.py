"""Tool: fetch the transaction under evaluation. First step of every agent run."""
from langchain_core.tools import tool


def make_get_transaction_tool(db):
    """Factory that closes over `db` so the resulting Tool's schema only
    exposes what the caller actually needs to supply (transaction_id)."""

    @tool
    def get_transaction(transaction_id: str) -> dict:
        """Fetch the transaction to evaluate by its tx_id."""
        document = db.transactions.find_one({"tx_id": transaction_id}, {"_id": 0})
        if not document:
            raise LookupError(f"Transaction not found: {transaction_id}")
        return document

    return get_transaction
