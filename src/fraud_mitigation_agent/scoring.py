from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionPolicy:
    approve_max: float = 39
    step_up_max: float = 69


def _bounded(value):
    return max(0.0, min(100.0, float(value)))


def vector_risk_score(similarity_score: float):
    # Cosine similarity [-1, 1] -> risk contribution [0, 100].
    return _bounded((float(similarity_score) + 1.0) * 50.0)


def rules_risk_score(triggered_rules: list[dict]):
    severity = {"low": 15, "medium": 30, "high": 50, "critical": 70}
    return _bounded(sum(severity.get(rule.get("severity", "medium"), 30) for rule in triggered_rules))


def signals_risk_score(signals: list[dict]):
    return _bounded(sum(float(signal.get("score", 0)) for signal in signals))


def score_components(vector_score, signals, triggered_rules, weights=None):
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
    policy = policy or DecisionPolicy()
    score = float(risk_score)
    if score <= policy.approve_max:
        return "APPROVE"
    if score <= policy.step_up_max:
        return "STEP-UP"
    return "DENY"


def build_reason_codes(signals, triggered_rules, similarity_results):
    codes = [x.get("code") for x in signals + triggered_rules if x.get("code")]
    if similarity_results and float(similarity_results[0].get("score", 0)) >= 0.75:
        codes.append("fraud_similarity")
    return list(dict.fromkeys(codes))
