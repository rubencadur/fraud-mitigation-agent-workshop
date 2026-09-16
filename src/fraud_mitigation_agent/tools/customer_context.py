from ._common import run_tool


def get_customer_state(db, customer_id):
    def work():
        document = db.customer_state.find_one({"customer_id": customer_id}, {"_id": 0})
        if not document:
            raise LookupError(f"Customer state not found: {customer_id}")
        return document
    return run_tool("get_customer_state", work)
