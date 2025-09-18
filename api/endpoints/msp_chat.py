from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
# from pygments.styles.dracula import background

from core.config import GOOGLE_API, CLAUDE_API, OPENAI_API, FRIENDLI_API
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from database.session import get_db
from crud.msp_chat import *
from langchain_service.embedding.get_vector import text_to_vector
from service.prompt import preview_prompt, user_input_intent, get_answer_with_knowledge
import core.config as config


chat_router = APIRouter(tags=["msp_chat"], prefix="/MSP_CHAT")


@chat_router.post("/msp_read_chat_session_by_user")
async def msp_read_chat_session_by_user(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")
    sessions = get_sessions_by_user(db, user_id)
    return {
        "status": True,
        "sessions": sessions
    }


@chat_router.post("/msp_request_message")
async def msp_request_message(
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    body = await request.json()
    user_input = body.get("user_input")
    chat_model = body.get("chat_model")
    session_id = body.get("session_id")
    user_id = body.get("user_id")
    role = body.get("role")
    project_id = body.get("project_id")
    knowledge_ids = body.get("knowledge_ids")
    title = None
    # print("참고 지식 ID : ",knowledge_ids)

    # 새로운 세션 생성 및 전달
    if session_id == 0:
        result = preview_prompt(user_input)
        preview = result.get("preview")
        title = result.get("title")

        new_session = create_session(
            db=db,
            user_id=user_id,
            project_id=project_id,
            title=title,
            preview=preview
        )
        session_id = new_session.id

    # 사용자 input vector로 변화
    vector_memory = text_to_vector(user_input)

    if knowledge_ids:
        print("================================지식베이스 참고 시작================================")
        knowledge_rows = get_similarity_search_by_knowledge_ids(
            db=db,
            knowledge_ids=knowledge_ids,
            user_input=user_input
        )

    # 사용자 메시지 저장 (즉시 저장)
    user_message = create_message(
        db,
        session_id=session_id,
        role=role,
        content=user_input,
        vector_memory=vector_memory
    )

    # 사용자 메시지에대한 llm추천
    # result = user_input_intent(user_input)
    # recommended_model = result.get("recommended_model")
    # print(recommended_model)

    # LLM답변 요청
    try:
        if chat_model in config.GOOGLE_MODELS:
            google_assistant = ChatGoogleGenerativeAI(
                model=chat_model,
                api_key=GOOGLE_API
            )
            if knowledge_ids:
                with_knowledge_prompt = get_answer_with_knowledge(google_assistant, user_input, knowledge_rows)
                response = with_knowledge_prompt
            else:
                invoke_result = google_assistant.invoke(user_input)
                response = invoke_result.content

        elif chat_model in config.ANTHROPIC_MODELS:
            anthropic_assistant = ChatAnthropic(
                model=chat_model,
                api_key=CLAUDE_API
            )
            if knowledge_ids:
                with_knowledge_prompt = get_answer_with_knowledge(anthropic_assistant, user_input, knowledge_rows)
                response = with_knowledge_prompt
            else:
                invoke_result = anthropic_assistant.invoke(user_input)
                response = invoke_result.content

        elif chat_model in config.OPENAI_MODELS:
            openai_assistant = ChatOpenAI(
                model=chat_model,
                api_key=OPENAI_API
            )
            if knowledge_ids:
                with_knowledge_prompt = get_answer_with_knowledge(openai_assistant, user_input, knowledge_rows)
                response = with_knowledge_prompt
            else:
                invoke_result = openai_assistant.invoke(user_input)
                response = invoke_result.content
        elif chat_model in config.FRIENDLI_MODELS:
            friendly_assistant = ChatOpenAI(
                api_key=FRIENDLI_API,
                model="LGAI-EXAONE/EXAONE-4.0-32B",
                base_url="https://api.friendli.ai/serverless/v1",
            )
            if knowledge_ids:
                with_knowledge_prompt = get_answer_with_knowledge(friendly_assistant, user_input, knowledge_rows)
                response = with_knowledge_prompt
            else:
                invoke_result = friendly_assistant.invoke(user_input)
                response = invoke_result.content

        else:
            response = f"선택한 모델({chat_model})이 지원되지 않습니다."
    except Exception as e:
        print(f"Error: {e}")  # 로그 확인용
        response = "오류가 발생했습니다. 관리자에 문의해주세요"

    # AI 응답 저장 (백그라운드로 저장 가능)
    background_tasks.add_task(
        create_message,
        db,
        session_id=session_id,
        role="assistant",
        content=response
    )
    # 답변 프론트로 리턴
    return {
        "status": "success",
        "user_message_id": user_message.id,
        "response": response,
        "session_id": session_id,
        "title": title
    }


@chat_router.post("/msp_read_message_by_session")
async def msp_read_message_by_session(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    session_id = body.get("session_id")
    messages = get_messages_by_session(db, session_id)
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "extra_data": m.extra_data,
            "created_at": m.created_at,
        }
        for m in messages
    ]

    # messages = get_messages_by_session(db, session_id)
    # return {
    #     "status": True,
    #     "messages": messages
    # }

