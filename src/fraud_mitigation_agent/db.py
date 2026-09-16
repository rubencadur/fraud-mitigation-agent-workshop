"""Thin wrappers around pymongo for connecting to a real MongoDB Atlas cluster.

`local.py` provides an in-memory drop-in with the same collection interface,
so the rest of the codebase never needs to know whether it's talking to Atlas
or to the offline fallback used when `MONGODB_URI` is not configured.
"""
from pymongo import MongoClient


def get_client(uri: str, timeout_ms: int = 10000):
    if not uri:
        raise ValueError("MONGODB_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
    # Fail fast with a clear error instead of a lazy timeout on the first real query.
    client.admin.command("ping")
    return client


def get_database(client, database_name: str):
    return client[database_name]


def get_collections(db):
    # Central list of the collections this workshop reads/writes, kept here
    # so notebooks can fetch all of them in one call instead of repeating names.
    names = [
        "transactions",
        "customer_state",
        "fraud_patterns",
        "risk_rules_config",
        "final_outcome",
        "risk_evidence",
    ]
    return {name: db[name] for name in names}
