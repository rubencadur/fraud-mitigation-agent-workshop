"""Builds the evidence document persisted for every scored transaction.

This is the audit trail: enough detail (components, weights, signals, rules,
similarity, full tool trace) to reconstruct *why* a decision was made without
re-running the agent, and to support a future human review or feedback loop.
"""
from datetime import datetime, timezone
import uuid


def make_evidence(transaction_id, score_result, decision, signals, rules, similarity, trace=None, config_version="demo-v1", policy_version="risk-v1"):
    return {
        "evidence_id": f"evidence-{transaction_id}-{uuid.uuid4().hex[:8]}",
        "transaction_id": transaction_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "risk_score": score_result["risk_score"],
        "components": score_result["components"],
        "weights": score_result["weights"],
        "signals": signals,
        "triggered_rules": rules,
        "similarity": similarity,
        "trace": trace or [],
        "config_version": config_version,
        "policy_version": policy_version,
        "source_tag": "fraud_mitigation_agent_workshop",
    }


def persist_evidence(collection, evidence):
    # Copy so the caller's in-memory `evidence` dict is never mutated by the
    # insert (both InMemoryCollection and pymongo add an _id on insert).
    document = dict(evidence)
    result = collection.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
