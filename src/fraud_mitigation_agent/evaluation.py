"""Precision/recall evaluation against the synthetic `ground_truth_fraud` labels.

Used only for the "advanced" evaluation notebook — never as a decision input,
since ground truth is a fixture label that would not exist for a real,
un-scored transaction.
"""
from .agent import FraudAgent


def binary_metrics(rows):
    # DENY is treated as the agent's "positive" (fraud) prediction; STEP-UP
    # and APPROVE both count as a negative prediction for this simple metric.
    tp = sum(1 for row in rows if row["truth"] and row["predicted"])
    tn = sum(1 for row in rows if not row["truth"] and not row["predicted"])
    fp = sum(1 for row in rows if not row["truth"] and row["predicted"])
    fn = sum(1 for row in rows if row["truth"] and not row["predicted"])
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "precision": precision, "recall": recall}


def evaluate_transactions(db, transaction_ids=None):
    """Run the full agent over every (or selected) transaction and score the results.

    persist=False so evaluation runs never write to final_outcome/risk_evidence
    alongside real decisions.
    """
    ids = transaction_ids or [x["tx_id"] for x in db.transactions.find({}, {"_id": 0, "tx_id": 1})]
    agent = FraudAgent(db)
    rows = []
    for tx_id in ids:
        tx = db.transactions.find_one({"tx_id": tx_id}, {"_id": 0})
        result = agent.analyze(tx_id, persist=False)
        decision = result.get("data", {}).get("decision")
        rows.append({"tx_id": tx_id, "truth": bool(tx.get("ground_truth_fraud")), "predicted": decision == "DENY", "decision": decision, "risk_score": result.get("data", {}).get("risk_score")})
    return {"rows": rows, "metrics": binary_metrics(rows)}
