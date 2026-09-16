"""Shared instrumentation wrapper used by every tool in this package.

Every tool function in transactions.py, rules.py, behavior.py, similarity.py
and decisions.py defers its real work into an inner `work()` closure and
hands it to `run_tool`, so timing and error handling is written once instead
of repeated in each tool.
"""
import time
from ..models import ToolResult


def run_tool(name, fn):
    """Time `fn()`, catch any exception, and always return a ToolResult.

    A tool never raises to its caller — a failure becomes
    status="error" in the trace instead, so one failing tool doesn't crash
    the whole agent run and is still visible in the audit trail.
    """
    started = time.perf_counter()
    try:
        result = fn()
        if isinstance(result, ToolResult):
            result.latency_ms = (time.perf_counter() - started) * 1000
            return result
        return ToolResult(name, data=result, latency_ms=(time.perf_counter() - started) * 1000)
    except Exception as exc:
        return ToolResult(name, status="error", error=str(exc), latency_ms=(time.perf_counter() - started) * 1000)
