from pymongo import MongoClient


def get_client(uri: str, timeout_ms: int = 10000):
    if not uri:
        raise ValueError("MONGODB_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
    client.admin.command("ping")
    return client


def get_database(client, database_name: str):
    return client[database_name]


def get_collections(db):
    names = [
        "transactions",
        "customer_state",
        "fraud_patterns",
        "risk_rules_config",
        "final_outcome",
        "risk_evidence",
    ]
    return {name: db[name] for name in names}
