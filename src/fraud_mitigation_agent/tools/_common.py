"""Shared instrumentation wrapper used by every tool in this package.

Every tool in transactions.py, customer_context.py, rules.py, behavior.py,
similarity.py and decisions.py is a LangChain `@tool` (built via a
`make_xxx_tool(...)` factory so it can close over `db`), invoked through
`run_tool` so timing and error handling is written once instead of repeated
in each tool. `graph.py` is what decides the fixed order these get called in
— never the LLM.
"""
import time
from ..models import ToolResult


def run_tool(name, langchain_tool, tool_input):
    """Invoke a LangChain tool and always return a ToolResult.

    `langchain_tool` is an object created with `@tool`, so it's called via
    `.invoke(tool_input)` — LangChain's calling convention — rather than as
    a plain function. `tool_input` is a dict whose keys match the wrapped
    function's parameter names.

    A tool never raises to its caller — a failure becomes status="error" in
    the trace instead, so one failing tool doesn't crash the whole agent run
    and is still visible in the audit trail.
    """
    started = time.perf_counter()
    try:
        result = langchain_tool.invoke(tool_input)
        return ToolResult(name, data=result, latency_ms=(time.perf_counter() - started) * 1000)
    except Exception as exc:
        return ToolResult(name, status="error", error=str(exc), latency_ms=(time.perf_counter() - started) * 1000)
