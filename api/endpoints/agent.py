from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from database.session import get_db

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.llm import Provider, AIModel
from models.agent import Agent

from fastapi.responses import JSONResponse
from langchain_service.agent.writing_agent import *
from fastapi import Request
from crud.llm import *
from schemas.agent import *
from langchain_service.chain.file_chain import get_file_chain
from langchain_service.chain.qa_chain import qa_chain, process_usage_in_background, get_session_title
from langchain_service.prompt.file_agent import get_file_agent
from langchain_service.embedding.get_vector import text_to_vector
from langchain_service.chain.image_generator import *
from langchain_service.vision.download_image import save_image_from_url
from langchain_service.agent.code_agent import code_agent
import core.config as config
from fastapi import BackgroundTasks
from service.sms.generate_random_code import generate_verification_code
from core.config import EMBEDDING_API
import os

from core.config import EMBEDDING_API

agent_router = APIRouter()

#### Agent 타입 정의

# @agent_router.post("/agents", response_model=AgentResponse)
# def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
#     # 1) provider 해석
#     provider_id = payload.provider_id
#     if not provider_id and payload.provider_name:
#         provider = db.execute(
#             select(Provider).where(Provider.name == payload.provider_name)
#         ).scalar_one_or_none()
#         if not provider:
#             raise HTTPException(422, detail="존재하지 않는 provider_name")
#         provider_id = provider.id
#
#     # 2) model 해석
#     model_id = payload.model_id
#     model_obj = None
#     if not model_id and payload.model_name:
#         model_obj = db.execute(
#             select(AIModel).where(AIModel.model_name == payload.model_name)
#         ).scalar_one_or_none()
#         if not model_obj:
#             raise HTTPException(422, detail="존재하지 않는 model_name")
#         model_id = model_obj.id
#
#     # 3) provider-model 일관성 체크(선택)
#     if model_id:
#         model_obj = model_obj or db.get(AIModel, model_id)
#         if not model_obj:
#             raise HTTPException(422, detail="유효하지 않은 model_id")
#         if provider_id and model_obj.provider_id != provider_id:
#             raise HTTPException(422, detail="provider_id와 model_id의 제공자가 일치하지 않습니다.")
#
#     # 4) 저장
#     agent = Agent(
#         id=... ,  # id 생성 로직
#         name=payload.name,
#         type=payload.type.value,
#         status="active",
#         provider_id=provider_id,
#         model_id=model_id,
#         avatar=payload.avatar,
#         description=payload.description,
#         capabilities=payload.capabilities or [],
#     )
#     db.add(agent)
#     db.commit()
#     db.refresh(agent)
#
#     # 5) 응답 확장(이름 포함)
#     prov = db.get(Provider, agent.provider_id) if agent.provider_id else None
#     mdl = db.get(AIModel, agent.model_id) if agent.model_id else None
#
#     return AgentResponse(
#         id=agent.id,
#         name=agent.name,
#         type=agent.type,
#         status=agent.status,
#         avatar=agent.avatar,
#         description=agent.description,
#         capabilities=agent.capabilities or [],
#         provider_id=agent.provider_id,
#         provider_name=prov.name if prov else None,
#         model_id=agent.model_id,
#         model_name=mdl.model_name if mdl else None,
#         created_at=agent.created_at,
#         last_active=agent.last_active,
#         tasks_completed=getattr(agent, "stats", None).tasks_completed if getattr(agent, "stats", None) else 0,
#         success_rate=getattr(agent, "stats", None).success_rate if getattr(agent, "stats", None) else 0.0,
#     )


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
        "structure" : response["structure"],
        "result" : response["result"],
        "quality" : response["quality"]
    })

