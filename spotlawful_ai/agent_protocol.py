from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class AgentRequest:
    request_id: str
    agent_name: str
    payload: Dict[str, Any]
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(
        cls,
        agent_name: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "AgentRequest":
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            agent_name=agent_name,
            payload=payload,
            user_id=user_id,
            metadata=metadata or {},
        )


@dataclass
class AgentFeedback:
    agent_name: str
    request_id: str
    feedback: str
    rating: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    agent_name: str
    request_id: str
    status: str
    result: Dict[str, Any]
    feedback_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.feedback_log: List[AgentFeedback] = []

    @abstractmethod
    def handle(self, request: AgentRequest) -> AgentResponse:
        raise NotImplementedError

    def record_feedback(self, feedback: AgentFeedback) -> None:
        self.feedback_log.append(feedback)

    def feedback_count(self) -> int:
        return len(self.feedback_log)

    def build_response(
        self,
        request: AgentRequest,
        result: Dict[str, Any],
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        return AgentResponse(
            agent_name=self.agent_name,
            request_id=request.request_id,
            status=status,
            result=result,
            feedback_count=self.feedback_count(),
            metadata=metadata or {},
        )
