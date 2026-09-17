"""Tool: detect statistical deviations from the customer's own baseline.

Distinct from rules.py: rules apply the same fixed thresholds to everyone,
while these signals are relative to *this* customer's normal behavior (e.g.
"5x this customer's average", not a fixed dollar amount).
"""
from langchain_core.tools import tool


def make_analyze_behavior_tool():
    """No `db` access here, so — unlike the other tools — this factory takes
    no arguments to close over."""

    @tool
    def analyze_behavior(transaction: dict, customer_state: dict) -> dict:
        """Detect statistical deviations from the customer's own baseline."""
        signals = []
        amount = float(transaction.get("amount", 0))
        average = float(customer_state.get("avg_amount", 0))
        # `average` guard: a brand-new customer with avg_amount=0 has no
        # baseline to deviate from, so skip rather than false-flag everything.
        if average and amount > average * 5:
            signals.append({"code": "amount_deviation", "score": 35, "detail": f"{amount} > 5x average {average}"})
        if transaction.get("ip") not in customer_state.get("usual_ips", []):
            signals.append({"code": "ip_deviation", "score": 20, "detail": "IP outside usual set"})
        if transaction.get("device_id") not in customer_state.get("usual_devices", []):
            signals.append({"code": "device_deviation", "score": 25, "detail": "device outside usual set"})
        geo = float(transaction.get("geo_km_from_usual", 0))
        if geo > 500:
            signals.append({"code": "geo_deviation", "score": 25, "detail": f"{geo} km"})
        return {"signals": signals, "baseline": {"avg_amount": average, "p95_amount": customer_state.get("p95_amount")}}

    return analyze_behavior
