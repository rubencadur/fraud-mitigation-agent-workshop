import time
from ..models import ToolResult


def run_tool(name, fn):
    started = time.perf_counter()
    try:
        result = fn()
        if isinstance(result, ToolResult):
            result.latency_ms = (time.perf_counter() - started) * 1000
            return result
        return ToolResult(name, data=result, latency_ms=(time.perf_counter() - started) * 1000)
    except Exception as exc:
        return ToolResult(name, status="error", error=str(exc), latency_ms=(time.perf_counter() - started) * 1000)
