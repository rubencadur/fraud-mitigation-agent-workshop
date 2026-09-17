"""Tool: fetch the customer's known baseline (usual devices/IPs/amounts).

This is what turns a transaction from an isolated event into something that
can be compared against "normal for this customer" — the input every other
downstream tool (rules, behavior) needs.
"""
from langchain_core.tools import tool


def make_get_customer_state_tool(db):
    @tool
    def get_customer_state(customer_id: str) -> dict:
        """Fetch the customer's known baseline (usual devices, IPs, amounts)."""
        document = db.customer_state.find_one({"customer_id": customer_id}, {"_id": 0})
        if not document:
            raise LookupError(f"Customer state not found: {customer_id}")
        return document

    return get_customer_state
