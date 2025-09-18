import core.config as config
import os
from langchain_service.agent.raect_agent import build_agent_with_history, create_agent_executor

# agent_router = APIRouter(prefix="/agent", tags=["agent"])

# =======================================
# ⚙️ Agent 생성 (초안, 주석 처리 상태)
# - provider / model 해석 및 검증
# - Agent 객체 생성 후 DB 저장
# - 응답은 AgentResponse
# =======================================
# @agent_router.post("/agents", response_model=AgentResponse)
# def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
#     # 1) provider 해석 (provider_id 또는 provider_name)
#     ...
#     # 2) model 해석 (model_id 또는 model_name)
#     ...
#     # 3) provider-model 일관성 체크
#     ...
#     # 4) Agent 저장
#     ...
#     # 5) Provider/Model 이름 포함 응답 확장
#     ...


from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.session import get_db

# ===== Models / CRUD / Schemas =====
from models.llm import Provider, AIModel
from models.agent import Agent, AgentTypeRef
from crud.agent import (
    create_agent, get_agent, get_agents,
    update_agent_status, delete_agent,
    update_agent_stats, update_agent_settings,
    get_agent_types)

from schemas.agent import (
    AgentCreate, AgentResponse,
    AgentStatusUpdate, AgentSettingsUpdate, AgentStatsUpdate,
    AgentRunRequest, AgentRunResponse,
    WriteAgentStep2Request
)

# ===== Agent runtimes =====
from langchain_service.agent.writing_agent import creative_writing_agent
from langchain_service.agent.code_agent import code_agent

from core.config import EMBEDDING_API
import uuid

agent_router = APIRouter(tags=["agents"], prefix="/agents")


# =======================================
# 내부 유틸: 에이전트 ID 생성
# =======================================
def _gen_agent_id() -> str:
    # models.agent.Agent.id: String(50). UUID로 충돌 위험 최소화
    return "agt_" + uuid.uuid4().hex[:24]


# =======================================
# 타입 조회 (lookup)
# =======================================
@agent_router.get("/types")
def list_agent_types(db: Session = Depends(get_db)):
    """AgentTypeRef 전체 조회"""    ## prefix + 엔드포인트 각라우터 프리픽스로
    return get_agent_types(db)


# =======================================
# 생성
# - provider/model 유효성, type 존재성 검증
# =======================================
@agent_router.post("", response_model=AgentResponse, status_code=201)
def create_agent_endpoint(payload: AgentCreate, db: Session = Depends(get_db)):
    # 타입 검증
    type_row = db.execute(select(AgentTypeRef).where(AgentTypeRef.code == payload.type.value)).scalar_one_or_none()
    if not type_row:
        raise HTTPException(422, detail="유효하지 않은 agent type")

    # provider/model 검증(선택적)
    if payload.provider_id:
        prov = db.get(Provider, payload.provider_id)
        if not prov:
            raise HTTPException(422, detail="provider_id 없음")

    if payload.model_id:
        mdl = db.get(AIModel, payload.model_id)
        if not mdl:
            raise HTTPException(422, detail="model_id 없음")
        if payload.provider_id and mdl.provider_id != payload.provider_id:
            raise HTTPException(422, detail="provider_id와 model_id의 제공자가 다름")

    agent_id = payload.id or _gen_agent_id()
    agent = create_agent(
        db=db,
        id=agent_id,
        name=payload.name,
        type_code=payload.type.value,
        avatar=payload.avatar,
        description=payload.description,
        provider_id=payload.provider_id,
        model_id=payload.model_id,
        capabilities=payload.capabilities,
    )
    return agent


# =======================================
# 목록 조회 (페이징)
#   /agents?limit=20&offset=0
# =======================================
@agent_router.get("", response_model=list[AgentResponse])
def list_agents_endpoint(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    items = get_agents(db)[offset: offset + limit]
    return items


# =======================================
# 단건 조회
# =======================================
@agent_router.get("/{agent_id}", response_model=AgentResponse)
def get_agent_endpoint(agent_id: str, db: Session = Depends(get_db)):
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(404, detail="Agent not found")
    return agent


# =======================================
# 상태 변경
#  - payload.status: "active" | "inactive"
# =======================================
@agent_router.patch("/{agent_id}/status", response_model=AgentResponse)
def update_agent_status_endpoint(agent_id: str, payload: AgentStatusUpdate, db: Session = Depends(get_db)):
    updated = update_agent_status(db, agent_id, payload.status)
    if not updated:
        raise HTTPException(404, detail="Agent not found")
    return updated


# =======================================
# 설정 업데이트 (1:1)
# =======================================
@agent_router.put("/{agent_id}/settings")
def update_settings_endpoint(agent_id: str, payload: AgentSettingsUpdate, db: Session = Depends(get_db)):
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(404, detail="Agent not found")
    return update_agent_settings(db, agent_id, payload.max_tokens, payload.temperature, payload.search_depth)


# =======================================
# 통계 업데이트 (1:1)
# =======================================
@agent_router.put("/{agent_id}/stats")
def update_stats_endpoint(agent_id: str, payload: AgentStatsUpdate, db: Session = Depends(get_db)):
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(404, detail="Agent not found")
    return update_agent_stats(db, agent_id, payload.tasks_completed, payload.success_rate)


# =======================================
# 🗑삭제
# =======================================
@agent_router.delete("/{agent_id}")
def delete_agent_endpoint(agent_id: str, db: Session = Depends(get_db)):
    ok = delete_agent(db, agent_id)
    if not ok:
        raise HTTPException(404, detail="Agent not found")
    return JSONResponse(content={"message": "Agent deleted"})


# =======================================
# ✍️ WritingAgent Step1 (기존 유지)
# =======================================
@agent_router.post("/WriteAgentStep1")
async def write_agent_ask_again_endpoint():
    resposne = f"""
    작문 에이전트를 실행합니다.
    고퀄리티의 작문을 위해 다음 정보들을 알려주세요.

    1. 글의 목적
    2. 주요 키워드
    3. 글의 대상 독자
    4. 문장의 톤과 스타일
    """
    return JSONResponse(content={"message": resposne})

# =======================================
# ✍️ WritingAgent Step2 (기존 유지)
# =======================================
@agent_router.post("/WriteAgentStep2")
async def extract_writing_intent_endpoint(request: WriteAgentStep2Request, db: Session = Depends(get_db)):
    message = request.message
    provider = "openai"
    model = "gpt-3.5-turbo"
    api_key = EMBEDDING_API

    response = creative_writing_agent(provider, model, api_key, message)

    print("\n============ 요구사항 ============\n")
    print(response["requirement"])
    print("\n============ 글의 구조 ============\n")
    print(response["structure"])
    print("\n============ 본문 ============\n")
    print(response["result"])
    print("\n============ 자체 평가 ============\n")
    print(response["quality"])

    return JSONResponse(content={
        "requirement": response["requirement"],
        "structure": response["structure"],
        "result": response["result"],
        "quality": response["quality"]
    })


# =======================================
# 🧩 공통 실행 라우트 (Dispatcher)
# - schemas.agent.AgentRunRequest/Response 필요
#   agent_type: research|coding|analysis|writing
#   provider/model 선택적
# =======================================
@agent_router.post("/run", response_model=AgentRunResponse)
def run_agent_endpoint(payload: AgentRunRequest, db: Session = Depends(get_db)):
    agent_type = payload.agent_type.value
    provider = payload.provider or "openai"
    model = payload.model or ("gpt-4o" if agent_type == "coding" else "gpt-4o-mini")
    api_key = payload.api_key or EMBEDDING_API

    # writing
    if agent_type == "writing":
        r = creative_writing_agent(provider, model, api_key, payload.message)
        return AgentRunResponse(
            agent_type=payload.agent_type,
            content=r["result"],
            artifacts={"outline": r["structure"]},
            meta={"quality": r["quality"]},
        )

    # coding
    if agent_type == "coding":
        if not payload.user_email:
            raise HTTPException(422, detail="coding 에이전트는 user_email 필요")
        r = code_agent(
            db=db,
            user_email=payload.user_email,
            provider=provider,
            model=model,
            api_key=api_key,
            message=payload.message,
        )
        return AgentRunResponse(agent_type=payload.agent_type, content=r)

    # research / analysis: 자리표시자
    if agent_type == "research":
        return AgentRunResponse(agent_type=payload.agent_type, content="research 에이전트 준비 중")
    if agent_type == "analysis":
        return AgentRunResponse(agent_type=payload.agent_type, content="analysis 에이전트 준비 중")

    raise HTTPException(400, detail="지원되지 않는 agent_type")


# DB에서 불러온 히스토리를 agent 메모리에 넣고, 새로운 입력(user_input)에 대한 응답을 생성
@agent_router.post("/msp_run_with_context")
async def msp_run_with_context(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    session_id = body.get("session_id")
    user_input = body.get("input")

    if not session_id or not user_input:
        raise HTTPException(status_code=400, detail="session_id와 input은 필수입니다.")

    # 1) AgentExecutor 생성 (tools는 실제 정의된 리스트 주입해야 함)
    tools = []  # TODO: 사용할 LangChain tools 리스트로 교체
    agent_executor = create_agent_executor(tools)

    # 2) DB 히스토리와 결합
    agent_with_history = build_agent_with_history(db, agent_executor)

    # 3) 실행
    response = agent_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )

    return {
        "status": True,
        "session_id": session_id,
        "response": response,
    }

