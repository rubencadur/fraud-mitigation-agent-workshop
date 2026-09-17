"""Tools: turn the outputs of every other tool into a final, evidenced decision."""
from langchain_core.tools import tool
from ..audit import make_evidence, persist_evidence
from ..scoring import score_components, decision_from_score, build_reason_codes


def make_score_and_decide_tool(db):
    @tool
    def score_and_decide(transaction_id: str, vector_score: float, signals: list, triggered_rules: list, similarity_results: list, trace: list) -> dict:
        """Combine similarity, behavioral signals and rules into a risk_score,
        a decision, and an auditable evidence document."""
        config = db.risk_rules_config.find_one({"config_id": "risk_rules_config"}, {"_id": 0}) or {}
        score_result = score_components(vector_score, signals, triggered_rules, config.get("weights"))
        decision = decision_from_score(score_result["risk_score"])
        reason_codes = build_reason_codes(signals, triggered_rules, similarity_results)
        evidence = make_evidence(
            transaction_id, score_result, decision, signals, triggered_rules, similarity_results,
            trace, config.get("version", "unknown"), "risk-v1",
        )
        return {
            "decision": decision, "risk_score": score_result["risk_score"],
            "components": score_result["components"], "reason_codes": reason_codes,
            "evidence": evidence, "config_version": config.get("version", "unknown"),
        }

    return score_and_decide


def make_persist_decision_tool(db):
    """Writes two documents: the full evidence (risk_evidence) and a compact
    outcome record (final_outcome) that's cheap to query for reporting. If
    `persist` is False, writes nothing — so analyze(persist=False) can be
    used for evaluation runs without touching the database."""

    @tool
    def persist_decision(transaction_id: str, decision: str, risk_score: float, reason_codes: list, evidence: dict, persist: bool) -> dict:
        """Persist the evidence and final outcome for a transaction, if persist=True."""
        if not persist:
            return {"outcome": None, "evidence_id": None, "persisted": False}
        stored_evidence = persist_evidence(db.risk_evidence, evidence)
        outcome = {
            "transaction_id": transaction_id,
            "decision": decision,
            "risk_score": risk_score,
            "reason_codes": reason_codes,
            "evidence_id": evidence["evidence_id"],
            "source_tag": "fraud_mitigation_agent_workshop",
        }
        db.final_outcome.replace_one({"transaction_id": transaction_id}, outcome, upsert=True)
        return {"outcome": outcome, "evidence_id": str(stored_evidence.get("_id")), "persisted": True}

    return persist_decision
