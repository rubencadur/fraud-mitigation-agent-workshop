from datetime import datetime, timezone
from .embeddings.manual import deterministic_embedding


def _pattern(tx_id, fraud_type, text):
    return {
        "tx_id": tx_id,
        "fraud_confirmed": True,
        "fraud_type": fraud_type,
        "fraud_signature_text": text,
        "embedding": deterministic_embedding(text),
        "source_tag": "fraud_mitigation_agent_synthetic",
    }


def demo_documents():
    patterns = [
        _pattern("pattern-001", "account_takeover", "new device new ip impossible travel odd hour credential reset high amount"),
        _pattern("pattern-002", "card_testing", "many small attempts new ip repeated velocity web checkout"),
        _pattern("pattern-003", "synthetic_identity", "new customer device mismatch unusual geo high amount mobile"),
        _pattern("pattern-004", "money_mule", "rapid transfer beneficiary new device distant geo unusual hour"),
    ]
    customers = [
        {
            "customer_id": "customer-normal",
            "usual_ips": ["198.51.100.10"],
            "usual_devices": ["device-normal-001"],
            "usual_countries": ["MX"],
            "avg_amount": 1200,
            "p95_amount": 4500,
            "transactions_24h": 3,
            "source_tag": "fraud_mitigation_agent_synthetic",
        },
        {
            "customer_id": "customer-stepup",
            "usual_ips": ["198.51.100.20"],
            "usual_devices": ["device-step-001"],
            "usual_countries": ["MX"],
            "avg_amount": 1800,
            "p95_amount": 9000,
            "transactions_24h": 4,
            "source_tag": "fraud_mitigation_agent_synthetic",
        },
        {
            "customer_id": "customer-risky",
            "usual_ips": ["198.51.100.30"],
            "usual_devices": ["device-risky-001"],
            "usual_countries": ["MX"],
            "avg_amount": 2500,
            "p95_amount": 12000,
            "transactions_24h": 2,
            "transactions_10m": 1,
            "source_tag": "fraud_mitigation_agent_synthetic",
        },
    ]
    transactions = [
        {
            "tx_id": "tx-normal-001", "customer_id": "customer-normal", "amount": 850,
            "currency": "MXN", "timestamp": "2025-01-15T16:20:00Z", "channel": "web",
            "ip": "198.51.100.10", "device_id": "device-normal-001", "geo_km_from_usual": 2,
            "ground_truth_fraud": False, "source_tag": "fraud_mitigation_agent_synthetic",
        },
        {
            "tx_id": "tx-stepup-001", "customer_id": "customer-stepup", "amount": 12000,
            "currency": "MXN", "timestamp": "2025-01-15T22:40:00Z", "channel": "mobile",
            "ip": "198.51.100.20", "device_id": "device-step-001", "geo_km_from_usual": 120,
            "ground_truth_fraud": False, "source_tag": "fraud_mitigation_agent_synthetic",
        },
        {
            "tx_id": "tx-risky-001", "customer_id": "customer-risky", "amount": 5000000,
            "currency": "COP", "timestamp": "2025-01-15T03:00:00Z", "channel": "mobile",
            "ip": "203.0.113.30", "device_id": "device-new-003", "geo_km_from_usual": 9000,
            "ground_truth_fraud": True, "source_tag": "fraud_mitigation_agent_synthetic",
        },
    ]
    rules = {
        "config_id": "risk_rules_config",
        "version": "demo-v1",
        "enabled": True,
        "thresholds": {
            "high_amount": 1000000,
            "amount_multiplier": 5,
            "impossible_travel_km": 500,
            "velocity_10m": 5,
        },
        "weights": {"vector": 0.40, "signals": 0.35, "rules": 0.25},
        "decision_thresholds": {"approve_max": 39, "step_up_max": 69},
        "source_tag": "fraud_mitigation_agent_synthetic",
    }
    return {"patterns": patterns, "customers": customers, "transactions": transactions, "rules": rules}


def seed_demo_data(db, reset=False):
    docs = demo_documents()
    collections = {
        "patterns": db["fraud_patterns"],
        "customers": db["customer_state"],
        "transactions": db["transactions"],
        "rules": db["risk_rules_config"],
    }
    if reset:
        for collection in collections.values():
            collection.delete_many({"source_tag": {"$in": ["fraud_mitigation_agent_synthetic", "fraud_mitigation_agent_colab_workshop"]}})
    for document in docs["patterns"]:
        collections["patterns"].replace_one({"tx_id": document["tx_id"]}, document, upsert=True)
    for document in docs["customers"]:
        collections["customers"].replace_one({"customer_id": document["customer_id"]}, document, upsert=True)
    for document in docs["transactions"]:
        document = dict(document)
        document["fraud_signature_text"] = (
            "new device new ip impossible travel odd hour high amount"
            if document["ground_truth_fraud"] else
            "familiar device familiar ip normal amount"
        )
        document["embedding"] = deterministic_embedding(document["fraud_signature_text"])
        collections["transactions"].replace_one({"tx_id": document["tx_id"]}, document, upsert=True)
    collections["rules"].replace_one({"config_id": docs["rules"]["config_id"]}, docs["rules"], upsert=True)
    return {key: len(value) if isinstance(value, list) else 1 for key, value in docs.items()}
