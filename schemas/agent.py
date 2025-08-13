from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Set
from datetime import datetime

from enum import Enum


# ==============================================================
# AGENT MODULE ROADMAP (구조 개요: 앞으로 채워 넣을 큰 틀)
# --------------------------------------------------------------
# 이 파일은 "에이전트 실행 요청 스키마"부터 시작하며,
# 이후 리서치/코딩/분석/글쓰기 에이전트 공통 구조를 담는 방향으로 확장

# 1) 에이전트 타입
#    - research:     웹/문서 리서치, 인용/출처 포함 요약
#    - coding:       코드 생성/리팩토링/테스트, 샌드박스 실행
#    - analysis:     데이터/통계 분석, 표/차트 아티팩트 생성
#    - writing:      아웃라인→초안→개정(스텝 기반) 글쓰기

class AgentType(str, Enum):
    research = "research"
    coding = "coding"
    analysis = "analysis"
    writing = "writing"


class AgentStatus(str, Enum):
    active = "active"  # 동작 중 (UI: 활성)
    inactive = "inactive"  # 비활성

# 상태 변화 규칙
ALLOWED_STATUS_TRANSITIONS: Dict[AgentStatus, Set[AgentStatus]] = {
    AgentStatus.active:   {AgentStatus.inactive},
    AgentStatus.inactive: {AgentStatus.active},
}

# 2) 공통 요청/응답 규격
# ====== 공통 베이스 ======
class AgentBase(BaseModel):
    name: str
    type: AgentType
    status: AgentStatus = AgentStatus.active
    avatar: str    # 모델 아이콘 .svg
    description: str
    provider_id: str    # models 와 일치 네이밍
    model_id: str
    capabilities: List[str] = None    # Agent 수행 기능 목록을 저장 하는 필드
    # capabilities: list[str] = Field(default_factory=list)

    @field_validator("capabilities", mode="before")    # None으로 들어오면, @field_validator가 실행 기본값채움
    @classmethod
    def _default_caps(cls, v):
        return v or []    # 기본값을 []로 채우는 역할

class AgentUpdate(BaseModel):
    name: str
    status: AgentStatus
    avatar: str
    description: str
    provider_id: str
    model_id: str
    capabilities: List[str]


class AgentResponse(AgentBase):
    id: str
    name: str
    type: AgentType
    status: AgentStatus
    avatar: str  # 모델 아이콘 .svg
    description: str
    capabilities: List[str] = None  # Agent 수행 기능 목록을 저장 하는 필드

    provider_id: str
    provider_name: str
    model_id: str
    model_name: str


    created_at: datetime   # DB에서 채워줌
    last_active: datetime
    tasks_completed: int = 0    # 완료된 작업 수
    success_rate: float = 0.0    # 완료작업/ 전체 수행 해야 할 작업 비율






# ====== status transition 요청 ======
class AgentStatusChangeRequest(BaseModel):
    agent_id: str
    from_status: AgentStatus
    to_status: AgentStatus

    @model_validator(mode="after")    # model 단위 검증_model_validator
    def _check_transition(self):
        allowed = ALLOWED_STATUS_TRANSITIONS.get(self.from_status, set())
        if self.to_status not in allowed:
            raise ValueError(f"활성/비활성 전이 불가: {self.from_status.value} → {self.to_status.value}")
        return self


####### LLM.PY 에서 FK로 provider 받아오기 ######

#    - Request: agent_type, message, project_id, session_id, provider, model,
#               parameters(temperature/top_p...), tools, attachments
#    - Response: content, artifacts(code/table/chart/json/text), citations, usage


# 3) 라이프사이클(모든 에이전트 공통)
#    - prepare: 컨텍스트 수집(세션/메모리/RAG), 프롬프트 구성
#    - run:     LLM 호출(+필요 시 tool 호출)
#    - post:    결과 정규화(content/artifacts/citations/usage)
#
# 4) 툴(추후 주입, 독립 모듈)
#    - web_search, url_reader, pdf_reader, code_runner, sql_runner, table_maker, citation
#    - 각 툴은 입력/출력 Pydantic 모델로 IO 계약 명확화
#
# 5) 프로바이더/모델 레지스트리
#    - provider_registry: 공급자별 클라이언트/모델 매핑
#    - parameter_mapper: 공급자별 파라미터 호환(temperature, top_p 등)
#
# 6) 메모리/RAG
#    - session_memory: 최근 대화 요약
#    - retriever(pgvector): 프로젝트 지식/문서 검색
#
# 7) 운영/안전장치
#    - 관측: run_id, 사용량, 툴 호출 로그, 지연시간
#    - 레이트/쿼터: user/project/provider 단위 제한
#    - 보안: 키 관리, PII/secret 레드액션, 권한검증
#
# 8) FastAPI 엔드포인트 (api/endpoints/agent.py)
#    - POST /agents/run → 공통 에이전트 실행
#    - (옵션) 스트리밍 응답, 작업 취소, 히스토리 조회
# ==============================================================


# --------------------------------------------------------------
# ✍️ Writing 에이전트 스텝2 요청
#    - message:        사용자가 원하는 글쓰기 지시/컨텍스트
#    - provider/model: 사용할 LLM 프로바이더/모델 지정
#    - api_key:        (임시) 외부 키 전달; 추후 서버 보관 키로 대체 권장
# --------------------------------------------------------------
class WriteAgentStep2Request(BaseModel):
    message: str
    provider: str
    model: str
    api_key: str

# ==============================================================
# 앞으로 추가될 섹션(주석만, 실제 코드는 추후 추가)
# --------------------------------------------------------------
# [A] BaseAgent (추상 인터페이스)
# class BaseAgent:
#     def prepare(self, context) -> str: ...
#     def run(self, prompt, tools) -> dict: ...
#     def postprocess(self, result) -> dict: ...

# [B] Agents 구현체
# class ResearchAgent(BaseAgent):  # 리서치 전용 프롬프트/후처리
#     pass
# class CodingAgent(BaseAgent):    # 코드 생성/리팩토링/테스트
#     pass
# class AnalysisAgent(BaseAgent):  # 데이터 분석/표/차트 산출
#     pass
# class WritingAgent(BaseAgent):   # 아웃라인→초안→개정
#     pass

# [C] Tools 인터페이스
# class ToolBase: ...
# class WebSearchTool(ToolBase): ...
# class CodeRunnerTool(ToolBase): ...
# class SqlRunnerTool(ToolBase): ...
# class PdfReaderTool(ToolBase): ...
# class CitationTool(ToolBase): ...

# [D] Provider/Model Runtime
# class ProviderRegistry: ...
# class ParameterMapper: ...
# class AgentExecutor: ...
#   - prepare(context) -> prompt
#   - call LLM(model/provider)
#   - route tools
#   - normalize response (content/artifacts/citations/usage)

# [E] Prompts 템플릿 (prompts/*.md)
# - research.md / coding.md / analysis.md / writing.md

# [F] Memory/RAG 통합
# - session_memory: 최근 k-turn 요약
# - retriever(pgvector): 프로젝트 문서 검색

# [G] Observability & Safety
# - run_id, latency, usage, tool_calls 로그
# - rate limit / quota
# - PII/secret redaction, 권한검증

# [H] FastAPI Endpoint 연결
# - POST /agents/run → AgentRunRequest → executor.run() → AgentRunResponse
# - 오류 시 표준 에러 스키마 반환

# [I] 테스트 전략
# - 단위: prepare/postprocess validator
# - 통합: mock provider/tool로 executor 경로 테스트
# - 회귀: 프롬프트 변경에 대한 골든 테스트
# ==============================================================
