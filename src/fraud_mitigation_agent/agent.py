"""Main orchestrator: runs a fixed-order LangGraph pipeline to reach a decision.

This is deliberately NOT an LLM-driven tool-calling loop. The seven tools
(transaction -> customer -> rules -> behavior -> similarity -> score/decide
-> persist) are wired into a `StateGraph` with hard-coded edges in
`graph.build_graph` — nothing in this class or in that graph lets an LLM
choose which node runs next. The LLM (via `self.provider`) is only ever
asked, after the graph finishes, to explain a decision already made by
deterministic code, so it can never skip a step, invent evidence, or change
the outcome.
"""
import re
import uuid
from .models import AgentResponse
from .llm.mock_provider import MockLLMProvider
from .graph import build_graph


class FraudAgent:
    """Small, explicit orchestrator used to teach tool-calling safely."""

    def __init__(self, db, provider=None):
        self.db = db
        # MockLLMProvider by default: the full analyze() pipeline below works
        # with zero API keys and zero network calls.
        self.provider = provider or MockLLMProvider()
        # Built once per agent: wiring the graph's nodes and edges doesn't
        # change between transactions, only the transaction_id passed to
        # .invoke() in analyze() does.
        self.graph = build_graph(db)

    def answer(self, prompt: str):
        """Free-form Q&A path (no transaction analysis, no graph involved) —
        used by notebook 01 to demonstrate that the LLM only ever produces
        prose, never a decision."""
        return self.provider.complete(prompt, system="You are the Fraud Mitigation Agent, a concise workshop assistant.")

    def analyze(self, transaction_id: str, persist: bool = True):
        """Run the full graph for one transaction and return the decision + trace."""
        # `trace` starts empty; AgentState's Annotated[list, operator.add]
        # reducer makes LangGraph concatenate each node's contribution onto
        # it instead of overwriting it.
        state = self.graph.invoke({"transaction_id": transaction_id, "trace": [], "persist": persist})
        if state.get("error"):
            # Every node after a failure is a no-op (see graph.py), so the
            # graph always reaches END even when a tool fails early.
            return AgentResponse("error", state["error"], state["trace"], str(uuid.uuid4())).as_dict()

        data = {
            "transaction_id": state["transaction"]["tx_id"],
            "decision": state.get("decision"),
            "risk_score": state.get("risk_score"),
            "components": state.get("components"),
            "reason_codes": state.get("reason_codes"),
            "evidence": state.get("evidence"),
            "config_version": (state.get("evidence") or {}).get("config_version"),
            "trace": state["trace"],
            "persisted": state.get("persisted", False),
        }
        # The LLM only narrates the already-final decision/score/reasons —
        # it cannot alter them, since they were computed before this call.
        content = self.provider.complete(
            f"Explain the fraud decision {data.get('decision')} with score {data.get('risk_score')} and reasons {data.get('reason_codes')}",
            system="Explain only the supplied deterministic evidence.",
        )
        return AgentResponse("final", content, state["trace"], str(uuid.uuid4()), data).as_dict()

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
