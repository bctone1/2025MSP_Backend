from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from database.session import get_db
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

