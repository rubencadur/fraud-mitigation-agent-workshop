"""Tool: fetch the transaction under evaluation. First step of every agent run."""
from ._common import run_tool


def get_transaction(db, transaction_id):
    def work():
        document = db.transactions.find_one({"tx_id": transaction_id}, {"_id": 0})
        if not document:
            raise LookupError(f"Transaction not found: {transaction_id}")
        return document
    return run_tool("get_transaction", work)
