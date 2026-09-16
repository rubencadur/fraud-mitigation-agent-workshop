"""Deterministic risk scoring and decisioning.

This is the one part of the pipeline the LLM is never allowed to influence:
given the same vector/signals/rules inputs, it always produces the same
risk_score and decision, which is what makes the final outcome auditable and
reproducible instead of dependent on a model's free-text response.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionPolicy:
    """Score thresholds that map a 0-100 risk_score to a decision band."""

    approve_max: float = 39
    step_up_max: float = 69
    # anything above step_up_max is DENY


def _bounded(value):
    return max(0.0, min(100.0, float(value)))


def vector_risk_score(similarity_score: float):
    # Cosine similarity [-1, 1] -> risk contribution [0, 100].
    return _bounded((float(similarity_score) + 1.0) * 50.0)


def rules_risk_score(triggered_rules: list[dict]):
    # Fixed point value per severity tier, summed across every rule that
    # fired (not averaged) — more triggered rules means more risk.
    severity = {"low": 15, "medium": 30, "high": 50, "critical": 70}
    return _bounded(sum(severity.get(rule.get("severity", "medium"), 30) for rule in triggered_rules))


def signals_risk_score(signals: list[dict]):
    # Behavioral signals already carry their own score (see tools/behavior.py);
    # this just sums and clamps them to the shared 0-100 scale.
    return _bounded(sum(float(signal.get("score", 0)) for signal in signals))


def score_components(vector_score, signals, triggered_rules, weights=None):
    """Combine the three risk sources into one weighted, explainable score.

    Each component is computed and reported individually (not just the
    final number) so the evidence document can show exactly how much each
    source contributed to the decision.
    """
    weights = weights or {"vector": 0.40, "signals": 0.35, "rules": 0.25}
    components = {
        "vector": round(vector_risk_score(vector_score), 4),
        "signals": round(signals_risk_score(signals), 4),
        "rules": round(rules_risk_score(triggered_rules), 4),
    }
    risk_score = sum(components[key] * float(weights.get(key, 0)) for key in components)
    return {
        "risk_score": round(_bounded(risk_score), 2),
        "components": components,
        "weights": weights,
        "formula": "Vector × 0.40 + Señales × 0.35 + Reglas × 0.25",
    }


def decision_from_score(risk_score, policy=None):
    """Map a risk_score to APPROVE / STEP-UP / DENY using DecisionPolicy thresholds."""
    policy = policy or DecisionPolicy()
    score = float(risk_score)
    if score <= policy.approve_max:
        return "APPROVE"
    if score <= policy.step_up_max:
        return "STEP-UP"
    return "DENY"


def build_reason_codes(signals, triggered_rules, similarity_results):
    """Human-readable codes for the evidence trail: why this decision, not just what."""
    codes = [x.get("code") for x in signals + triggered_rules if x.get("code")]
    if similarity_results and float(similarity_results[0].get("score", 0)) >= 0.75:
        # Best match only: a strong resemblance to one known fraud pattern is
        # itself a reportable reason, independent of the numeric score.
        codes.append("fraud_similarity")
    return list(dict.fromkeys(codes))
