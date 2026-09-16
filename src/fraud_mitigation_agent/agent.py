"""Main orchestrator: chains the tools in a fixed order to reach a decision.

This is deliberately NOT an LLM-driven tool-calling loop — the sequence
(transaction -> customer -> rules -> behavior -> similarity -> score/decide
-> persist) is hard-coded in `analyze()`. The LLM (via `self.provider`) is
only ever asked to explain a decision already made by deterministic code, so
it can never skip a step, invent evidence, or change the outcome.
"""
import re
import uuid
from .models import AgentResponse
from .llm.mock_provider import MockLLMProvider
from .tools.transactions import get_transaction
from .tools.customer_context import get_customer_state
from .tools.rules import evaluate_rules
from .tools.behavior import analyze_behavior
from .tools.similarity import find_similar_fraud
from .tools.decisions import score_and_decide, persist_decision


class FraudAgent:
    """Small, explicit orchestrator used to teach tool-calling safely."""

    def __init__(self, db, provider=None):
        self.db = db
        # MockLLMProvider by default: the full analyze() pipeline below works
        # with zero API keys and zero network calls.
        self.provider = provider or MockLLMProvider()

    def answer(self, prompt: str):
        """Free-form Q&A path (no transaction analysis) — used by notebook 01
        to demonstrate that the LLM only ever produces prose, never a decision."""
        return self.provider.complete(prompt, system="You are the Fraud Mitigation Agent, a concise workshop assistant.")

    def analyze(self, transaction_id: str, persist: bool = True):
        """Run the full fixed pipeline for one transaction and return the decision + trace."""
        trace = []
        tx_result = get_transaction(self.db, transaction_id)
        trace.append(tx_result.as_dict())
        if tx_result.status != "success":
            # Stop immediately: every later tool needs the transaction data,
            # so a missing transaction can't proceed further.
            return AgentResponse("error", tx_result.error, trace, str(uuid.uuid4())).as_dict()
        transaction = tx_result.data

        customer_result = get_customer_state(self.db, transaction["customer_id"])
        trace.append(customer_result.as_dict())
        # Missing customer state is tolerated (treated as an empty baseline)
        # rather than fatal, so a first-time customer can still be scored.
        customer = customer_result.data or {}

        rules_result = evaluate_rules(self.db, transaction, customer)
        trace.append(rules_result.as_dict())
        behavior_result = analyze_behavior(transaction, customer)
        trace.append(behavior_result.as_dict())
        # Behavioral signal codes (e.g. "amount_deviation") feed the fallback
        # text embedding when the transaction has no fraud_signature_text yet.
        similarity_result = find_similar_fraud(self.db, transaction, behavior_result.data.get("signals", []))
        trace.append(similarity_result.as_dict())

        decision_result = score_and_decide(
            self.db, transaction, behavior_result.data,
            rules_result.data, similarity_result.data, trace,
        )
        trace.append(decision_result.as_dict())
        persistence = None
        if persist and decision_result.status == "success":
            persistence = persist_decision(self.db, decision_result.data)
            trace.append(persistence.as_dict())

        data = decision_result.data if decision_result.status == "success" else {}
        data["trace"] = trace
        data["persisted"] = bool(persistence and persistence.status == "success")
        # The LLM only narrates the already-final decision/score/reasons —
        # it cannot alter them, since they were computed before this call.
        content = self.provider.complete(
            f"Explain the fraud decision {data.get('decision')} with score {data.get('risk_score')} and reasons {data.get('reason_codes')}",
            system="Explain only the supplied deterministic evidence.",
        )
        return AgentResponse("final", content, trace, str(uuid.uuid4()), data).as_dict()

    def run(self, prompt: str, persist: bool = True):
        """Very small router: if the prompt looks like it references a
        transaction id, analyze it; otherwise fall back to free-form answer()."""
        match = re.search(r"(?:tx|transaction)[-_ ]([a-z0-9]+(?:[-_][a-z0-9]+)*)", prompt.lower())
        if match:
            # Normalize whatever matched ("tx-123", "transaction 123", ...)
            # into the canonical "tx-<id>" format used as the document key.
            candidate = match.group(0).replace("transaction", "").replace("tx ", "tx-").strip()
            candidate = candidate.replace(" ", "-")
            if not candidate.startswith("tx-"):
                candidate = "tx-" + candidate
            return self.analyze(candidate, persist=persist)
        return AgentResponse("final", self.answer(prompt), [], str(uuid.uuid4())).as_dict()
