# Contratos

## TransactionInput

```json
{
  "transaction_id": "tx-risky-001",
  "customer_id": "customer-risky",
  "amount": 5000000,
  "currency": "COP",
  "timestamp": "2025-01-15T03:00:00Z",
  "channel": "mobile",
  "ip": "203.0.113.30",
  "device_id": "device-new-003",
  "geo_km_from_usual": 9000
}
```

## ToolResult

```json
{
  "tool_name": "get_customer_state",
  "status": "success",
  "data": {},
  "evidence": [],
  "latency_ms": 10,
  "error": null
}
```

## FraudDecision

```json
{
  "transaction_id": "tx-risky-001",
  "decision": "DENY",
  "risk_score": 88,
  "reason_codes": ["new_ip", "new_device", "fraud_similarity"],
  "evidence_id": "evidence-tx-risky-001",
  "config_version": "demo-v1",
  "policy_version": "risk-v1",
  "latency_ms": {"total": 80}
}
```
