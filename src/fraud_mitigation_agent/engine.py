"""Reference wrapper showing how `FraudAgent` would be called in a request path.

This is intentionally the thinnest possible layer: one call in, one call out.
It exists so the "advanced" notebook can demonstrate an end-to-end flow
without duplicating agent logic — it is not a queue consumer, API server, or
anything resembling a production realtime pipeline.
"""
from .agent import FraudAgent
from .config import Settings
from .db import get_client, get_database


class RealtimeFraudEngine:
    """Synchronous reference engine; production deployment needs queues, timeouts and observability."""

    def __init__(self, db, settings=None):
        self.db = db
        self.settings = settings or Settings.from_env()
        self.agent = FraudAgent(db)

    def evaluate(self, transaction_id, persist=True):
        result = self.agent.analyze(transaction_id, persist=persist)
        result["engine"] = "fraud_mitigation_agent-realtime-reference"
        return result


def run_from_uri(transaction_id, settings=None, persist=True):
    """Convenience one-shot: opens a fresh Atlas connection, evaluates, closes it.

    Meant for notebook cells / scripts, not for a long-running service where
    you'd want a pooled, reused client instead of connecting per call.
    """
    settings = settings or Settings.from_env()
    client = get_client(settings.mongodb_uri)
    try:
        db = get_database(client, settings.database_name)
        return RealtimeFraudEngine(db, settings).evaluate(transaction_id, persist=persist)
    finally:
        client.close()
