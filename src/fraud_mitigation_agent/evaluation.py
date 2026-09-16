from .agent import FraudAgent


def binary_metrics(rows):
    tp = sum(1 for row in rows if row["truth"] and row["predicted"])
    tn = sum(1 for row in rows if not row["truth"] and not row["predicted"])
    fp = sum(1 for row in rows if not row["truth"] and row["predicted"])
    fn = sum(1 for row in rows if row["truth"] and not row["predicted"])
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "precision": precision, "recall": recall}


def evaluate_transactions(db, transaction_ids=None):
    ids = transaction_ids or [x["tx_id"] for x in db.transactions.find({}, {"_id": 0, "tx_id": 1})]
    agent = FraudAgent(db)
    rows = []
    for tx_id in ids:
        tx = db.transactions.find_one({"tx_id": tx_id}, {"_id": 0})
        result = agent.analyze(tx_id, persist=False)
        decision = result.get("data", {}).get("decision")
        rows.append({"tx_id": tx_id, "truth": bool(tx.get("ground_truth_fraud")), "predicted": decision == "DENY", "decision": decision, "risk_score": result.get("data", {}).get("risk_score")})
    return {"rows": rows, "metrics": binary_metrics(rows)}
