from ._common import run_tool
from ..audit import make_evidence, persist_evidence
from ..scoring import score_components, decision_from_score, build_reason_codes


def score_and_decide(db, transaction, behavior_result, rules_result, similarity_result, trace=None):
    def work():
        similarity = (similarity_result.get("results") or [{}])[0]
        config = db.risk_rules_config.find_one({"config_id": "risk_rules_config"}, {"_id": 0}) or {}
        score_result = score_components(
            similarity.get("score", 0),
            behavior_result.get("signals", []),
            rules_result.get("triggered_rules", []),
            config.get("weights"),
        )
        decision = decision_from_score(score_result["risk_score"])
        reason_codes = build_reason_codes(
            behavior_result.get("signals", []),
            rules_result.get("triggered_rules", []),
            similarity_result.get("results", []),
        )
        evidence = make_evidence(
            transaction["tx_id"], score_result, decision,
            behavior_result.get("signals", []), rules_result.get("triggered_rules", []),
            similarity_result.get("results", []), trace,
            config.get("version", "unknown"), "risk-v1",
        )
        return {"transaction_id": transaction["tx_id"], "decision": decision, "risk_score": score_result["risk_score"], "components": score_result["components"], "reason_codes": reason_codes, "evidence": evidence, "config_version": config.get("version", "unknown")}
    return run_tool("score_and_decide", work)


def persist_decision(db, decision_result):
    def work():
        evidence = persist_evidence(db.risk_evidence, decision_result["evidence"])
        outcome = {
            "transaction_id": decision_result["transaction_id"],
            "decision": decision_result["decision"],
            "risk_score": decision_result["risk_score"],
            "reason_codes": decision_result["reason_codes"],
            "evidence_id": decision_result["evidence"]["evidence_id"],
            "source_tag": "fraud_mitigation_agent_workshop",
        }
        db.final_outcome.replace_one({"transaction_id": outcome["transaction_id"]}, outcome, upsert=True)
        return {"outcome": outcome, "evidence_id": str(evidence.get("_id"))}
    return run_tool("persist_decision", work)
