from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
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
