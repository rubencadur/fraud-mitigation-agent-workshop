"""Shared data shapes for tool execution and agent responses.

Every tool in `tools/` returns a `ToolResult` and every call is appended to a
"trace" list, so the full decision path (what was called, with what data, how
long it took, whether it failed) can be inspected and audited later.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Uniform envelope returned by every tool so the agent trace is consistent."""

    tool_name: str
    status: str = "success"
    data: Any = None
    evidence: list = field(default_factory=list)
    latency_ms: float = 0.0
    error: str | None = None

    def as_dict(self):
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "data": self.data,
            "evidence": self.evidence,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
        }


@dataclass
class AgentResponse:
    """Final payload returned by `FraudAgent`, including the full tool-call trace."""

    response_type: str
    content: str = ""
    tool_calls: list = field(default_factory=list)
    trace_id: str = ""
    data: dict = field(default_factory=dict)

    def as_dict(self):
        return {
            "type": self.response_type,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "trace_id": self.trace_id,
            "data": self.data,
        }
