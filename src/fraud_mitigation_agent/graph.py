"""Wires the agent's tools into a fixed-order LangGraph pipeline.

Every edge here is hard-coded in `build_graph`: transaction -> customer ->
rules -> behavior -> similarity -> score_and_decide -> persist_decision.
Nothing in this module lets an LLM pick which node runs next — that fixed
order is what keeps the fraud decision deterministic and auditable (see
PROJECT_SPECIFICATION.md section 19). The LLM only narrates the result,
outside this graph entirely (see agent.py).
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from .tools._common import run_tool
from .tools.transactions import make_get_transaction_tool
from .tools.customer_context import make_get_customer_state_tool
from .tools.rules import make_evaluate_rules_tool
from .tools.behavior import make_analyze_behavior_tool
from .tools.similarity import make_find_similar_fraud_tool
from .tools.decisions import make_score_and_decide_tool, make_persist_decision_tool


class AgentState(TypedDict, total=False):
    """State threaded through the graph. Each node reads what it needs and
    returns only the keys it wants to add or change; LangGraph merges that
    into the running state.

    `trace` uses `Annotated[list, operator.add]` as its reducer, so each
    node's contribution is concatenated onto the existing trace instead of
    replacing it — the default merge behavior for a plain `list` field would
    be "last write wins," which would silently drop every earlier node's
    trace entry.
    """

    transaction_id: str
    transaction: dict
    customer: dict
    rules_result: dict
    behavior_result: dict
    similarity_result: dict
    decision: str
    risk_score: float
    components: dict
    reason_codes: list
    evidence: dict
    persist: bool
    persisted: bool
    trace: Annotated[list, operator.add]
    error: str


def build_graph(db):
    """Build and compile the seven-node graph for one `db`.

    Tools are constructed once here (each via its `make_xxx_tool(db)`
    factory) and closed over by the node functions below, rather than
    rebuilt per transaction.
    """
    get_transaction_tool = make_get_transaction_tool(db)
    get_customer_state_tool = make_get_customer_state_tool(db)
    evaluate_rules_tool = make_evaluate_rules_tool(db)
    analyze_behavior_tool = make_analyze_behavior_tool()
    find_similar_fraud_tool = make_find_similar_fraud_tool(db)
    score_and_decide_tool = make_score_and_decide_tool(db)
    persist_decision_tool = make_persist_decision_tool(db)

    def node_get_transaction(state: AgentState) -> dict:
        result = run_tool("get_transaction", get_transaction_tool, {"transaction_id": state["transaction_id"]})
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        return {"trace": [result.as_dict()], "transaction": result.data}

    def node_get_customer_state(state: AgentState) -> dict:
        # Every node after the first starts with this guard: once a prior
        # step has failed, later nodes become no-ops (return {}) instead of
        # operating on incomplete state, and the graph drains to END.
        if state.get("error"):
            return {}
        customer_id = state["transaction"]["customer_id"]
        result = run_tool("get_customer_state", get_customer_state_tool, {"customer_id": customer_id})
        if result.status != "success":
            # A customer with no history (or not found) shouldn't halt the
            # analysis — treat it as an empty baseline, not a fatal error.
            return {"trace": [result.as_dict()], "customer": {}}
        return {"trace": [result.as_dict()], "customer": result.data}

    def node_evaluate_rules(state: AgentState) -> dict:
        if state.get("error"):
            return {}
        tool_input = {"transaction": state["transaction"], "customer_state": state.get("customer", {})}
        result = run_tool("evaluate_rules", evaluate_rules_tool, tool_input)
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        return {"trace": [result.as_dict()], "rules_result": result.data}

    def node_analyze_behavior(state: AgentState) -> dict:
        if state.get("error"):
            return {}
        tool_input = {"transaction": state["transaction"], "customer_state": state.get("customer", {})}
        result = run_tool("analyze_behavior", analyze_behavior_tool, tool_input)
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        return {"trace": [result.as_dict()], "behavior_result": result.data}

    def node_find_similar_fraud(state: AgentState) -> dict:
        if state.get("error"):
            return {}
        # Behavioral signal codes feed the fallback text embedding when the
        # transaction has no fraud_signature_text of its own.
        signal_codes = [s.get("code", "") for s in state.get("behavior_result", {}).get("signals", [])]
        tool_input = {"transaction": state["transaction"], "signal_codes": signal_codes}
        result = run_tool("find_similar_fraud", find_similar_fraud_tool, tool_input)
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        return {"trace": [result.as_dict()], "similarity_result": result.data}

    def node_score_and_decide(state: AgentState) -> dict:
        if state.get("error"):
            return {}
        # Only the best (first) similarity match feeds the score; the full
        # ranked list still goes into the evidence document.
        similarity = (state["similarity_result"].get("results") or [{}])[0]
        tool_input = {
            "transaction_id": state["transaction"]["tx_id"],
            "vector_score": similarity.get("score", 0),
            "signals": state["behavior_result"].get("signals", []),
            "triggered_rules": state["rules_result"].get("triggered_rules", []),
            "similarity_results": state["similarity_result"].get("results", []),
            "trace": state["trace"],
        }
        result = run_tool("score_and_decide", score_and_decide_tool, tool_input)
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        data = result.data
        return {
            "trace": [result.as_dict()], "decision": data["decision"], "risk_score": data["risk_score"],
            "components": data["components"], "reason_codes": data["reason_codes"], "evidence": data["evidence"],
        }

    def node_persist_decision(state: AgentState) -> dict:
        if state.get("error"):
            return {}
        tool_input = {
            "transaction_id": state["transaction"]["tx_id"],
            "decision": state["decision"],
            "risk_score": state["risk_score"],
            "reason_codes": state["reason_codes"],
            "evidence": state["evidence"],
            # `persist` comes from the initial state (set by FraudAgent.analyze),
            # never decided by this node or by an LLM.
            "persist": state.get("persist", True),
        }
        result = run_tool("persist_decision", persist_decision_tool, tool_input)
        if result.status != "success":
            return {"trace": [result.as_dict()], "error": result.error}
        return {"trace": [result.as_dict()], "persisted": result.data.get("persisted", False)}

    graph = StateGraph(AgentState)
    graph.add_node("get_transaction", node_get_transaction)
    graph.add_node("get_customer_state", node_get_customer_state)
    graph.add_node("evaluate_rules", node_evaluate_rules)
    graph.add_node("analyze_behavior", node_analyze_behavior)
    graph.add_node("find_similar_fraud", node_find_similar_fraud)
    graph.add_node("score_and_decide", node_score_and_decide)
    graph.add_node("persist_decision", node_persist_decision)
    graph.add_edge(START, "get_transaction")
    graph.add_edge("get_transaction", "get_customer_state")
    graph.add_edge("get_customer_state", "evaluate_rules")
    graph.add_edge("evaluate_rules", "analyze_behavior")
    graph.add_edge("analyze_behavior", "find_similar_fraud")
    graph.add_edge("find_similar_fraud", "score_and_decide")
    graph.add_edge("score_and_decide", "persist_decision")
    graph.add_edge("persist_decision", END)
    return graph.compile()
