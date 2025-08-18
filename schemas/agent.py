from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, field_validator, model_validator


# ==============================================================
# AGENT MODULE ROADMAP
# ==============================================================

# --------------------------------------------------------------
# 1) 에이전트 타입/상태 + 전이 규칙
# --------------------------------------------------------------
class AgentType(str, Enum):
    research = "research"   # 웹/문서 리서치
    coding   = "coding"     # 코드 생성/리팩토링/테스트
    analysis = "analysis"   # 데이터/통계 분석
    writing  = "writing"    # 글쓰기


class AgentStatus(str, Enum):
    active = "active"
    inactive = "inactive"


ALLOWED_STATUS_TRANSITIONS: Dict[AgentStatus, Set[AgentStatus]] = {
    AgentStatus.active:   {AgentStatus.inactive},
    AgentStatus.inactive: {AgentStatus.active},
}


# --------------------------------------------------------------
# 2) 공통 베이스/응답
#   - models.Agent 의 컬럼 타입에 맞춰 교정:
#     provider_id, model_id → int(Optional)
#     avatar, description → Optional[str]
# --------------------------------------------------------------
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: AgentType
    status: AgentStatus = AgentStatus.active
    avatar: Optional[str] = None              # 모델 아이콘 .svg 경로 등
    description: Optional[str] = None
    provider_id: Optional[int] = None         # FK → provider_table.id
    model_id: Optional[int] = None            # FK → ai_models.id
    capabilities: List[str]

    @field_validator("capabilities", mode="before")
    @classmethod
    def _caps_none_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)

    @field_validator("capabilities", mode="after")
    @classmethod
    def _caps_dedup(cls, v: List[str]):
        seen, out = set(), []
        for x in v:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out


class AgentResponse(AgentBase):
    id: str
    provider_name: Optional[str] = None
    model_name: Optional[str] = None

    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    tasks_completed: int = 0
    success_rate: float = 0.0


# --------------------------------------------------------------
# 3) 생성/수정/상태 변경 요청
# --------------------------------------------------------------
class AgentCreate(AgentBase):
    # 엔드포인트에서 제공 시 사용. 미제공 시 서버에서 생성(예: agt_xxx)
    id: Optional[str] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[AgentStatus] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    provider_id: Optional[int] = None
    model_id: Optional[int] = None
    capabilities: Optional[List[str]] = None

    @field_validator("capabilities", mode="before")
    @classmethod
    def _caps_none_to_list(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        return list(v)


class AgentStatusUpdate(BaseModel):
    status: AgentStatus


class AgentStatusChangeRequest(BaseModel):
    agent_id: str
    from_status: AgentStatus
    to_status: AgentStatus

    @model_validator(mode="after")
    def _check_transition(self):
        allowed = ALLOWED_STATUS_TRANSITIONS.get(self.from_status, set())
        if self.to_status not in allowed:
            raise ValueError(f"활성/비활성 전이 불가: {self.from_status.value} → {self.to_status.value}")
        return self


# --------------------------------------------------------------
# 4) 설정/통계 업데이트
# --------------------------------------------------------------
class AgentSettingsUpdate(BaseModel):
    max_tokens: Optional[int] = Field(default=None, ge=1)
    temperature: Optional[float] = Field(default=None)
    search_depth: Optional[str] = None


class AgentStatsUpdate(BaseModel):
    tasks_completed: int = Field(..., ge=0)
    success_rate: float = Field(..., ge=0.0, le=1.0)  # 0~1 사이 비율


# --------------------------------------------------------------
# 5) 실행 요청/응답 공통 (Dispatcher: /agents/run)
# --------------------------------------------------------------
class AgentRunRequest(BaseModel):
    agent_type: AgentType
    message: str

    # 선택 파라미터
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None

    # 컨텍스트(필요시 사용)
    user_email: Optional[str] = None
    project_id: Optional[int] = None
    session_id: Optional[str] = None

    # 선택적 샘플 파라미터
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None

    tools: Optional[List[str]] = None
    attachments: Optional[List[str]] = None


class AgentRunResponse(BaseModel):
    agent_type: AgentType
    content: str
    artifacts: Dict[str, object]   # code/table/chart/json/text 등
    citations: List[str]
    usage: Dict[str, object]
    meta: Dict[str, object]


# --------------------------------------------------------------
# 6) Writing 전용 요청 (기존 유지, 선택형으로 교정)
# --------------------------------------------------------------
class WriteAgentStep2Request(BaseModel):
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None


# --------------------------------------------------------------
# 7) 주석: 이후 확장 포인트
#   - BaseAgent 인터페이스, 개별 Agent 구현, Tool I/O 모델,
#     Registry, Memory/RAG, Observability/Safety 등
# --------------------------------------------------------------
# [A] BaseAgent (추상 인터페이스)
# class BaseAgent: ...
# [B] Agents 구현체
# class ResearchAgent(BaseAgent): ...
# class CodingAgent(BaseAgent): ...
# class AnalysisAgent(BaseAgent): ...
# class WritingAgent(BaseAgent): ...
# [C] Tools I/O 모델
# class WebSearchInput(BaseModel): ...
# class WebSearchOutput(BaseModel): ...
# [D] Registry / Mapper
# class ProviderBinding(BaseModel): ...
# [E] Memory/RAG
# class RetrievalQuery(BaseModel): ...
# [F] Observability
# class AgentRunLog(BaseModel): ...
