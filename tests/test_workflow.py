from fraud_mitigation_agent.agent import FraudAgent
from fraud_mitigation_agent.local import InMemoryDB
from fraud_mitigation_agent.synthetic import seed_demo_data


def test_offline_workflow_produces_auditable_decision():
    db = InMemoryDB()
    seed_demo_data(db, reset=True)
    result = FraudAgent(db).analyze("tx-risky-001", persist=True)
    assert result["data"]["decision"] in {"APPROVE", "STEP-UP", "DENY"}
    assert result["data"]["risk_score"] >= 0
    assert result["data"]["evidence"]["transaction_id"] == "tx-risky-001"
    assert db.final_outcome.find_one({"transaction_id": "tx-risky-001"}) is not None
    assert db.risk_evidence.find_one({"transaction_id": "tx-risky-001"}) is not None
