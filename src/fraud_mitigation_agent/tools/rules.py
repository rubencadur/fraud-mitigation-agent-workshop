from ._common import run_tool
from datetime import datetime


def get_rules_config(db):
    return run_tool("get_rules_config", lambda: db.risk_rules_config.find_one({"config_id": "risk_rules_config"}, {"_id": 0}))


def evaluate_rules(db, transaction: dict, customer_state: dict | None = None):
    def work():
        config = db.risk_rules_config.find_one({"config_id": "risk_rules_config"}, {"_id": 0}) or {}
        thresholds = config.get("thresholds", {})
        state = customer_state or {}
        triggered = []
        amount = float(transaction.get("amount", 0))
        if amount >= thresholds.get("high_amount", float("inf")):
            triggered.append({"code": "high_amount", "severity": "high", "detail": amount})
        if transaction.get("ip") not in state.get("usual_ips", []):
            triggered.append({"code": "new_ip", "severity": "medium", "detail": transaction.get("ip")})
        if transaction.get("device_id") not in state.get("usual_devices", []):
            triggered.append({"code": "new_device", "severity": "high", "detail": transaction.get("device_id")})
        if float(transaction.get("geo_km_from_usual", 0)) >= thresholds.get("impossible_travel_km", float("inf")):
            triggered.append({"code": "impossible_travel", "severity": "critical", "detail": transaction.get("geo_km_from_usual")})
        hour = int(transaction.get("timestamp", "T12:").split("T")[-1][:2] or 12)
        if hour < 6 or hour >= 23:
            triggered.append({"code": "odd_hour", "severity": "medium", "detail": hour})
        return {"triggered_rules": triggered, "config_version": config.get("version", "unknown"), "weights": config.get("weights", {})}
    return run_tool("evaluate_rules", work)
