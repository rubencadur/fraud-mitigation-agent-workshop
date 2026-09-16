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
    settings = settings or Settings.from_env()
    client = get_client(settings.mongodb_uri)
    try:
        db = get_database(client, settings.database_name)
        return RealtimeFraudEngine(db, settings).evaluate(transaction_id, persist=persist)
    finally:
        client.close()
