from fraud_mitigation_agent.scoring import decision_from_score, score_components


def test_score_formula_and_decision():
    result = score_components(0.8, [{"code": "new_device", "score": 25}], [{"code": "high_amount", "severity": "high"}])
    assert 0 <= result["risk_score"] <= 100
    assert result["formula"] == "Vector × 0.40 + Señales × 0.35 + Reglas × 0.25"
    assert decision_from_score(20) == "APPROVE"
    assert decision_from_score(50) == "STEP-UP"
    assert decision_from_score(80) == "DENY"
