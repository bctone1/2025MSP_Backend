from langchain_google_genai import ChatGoogleGenerativeAI
# from pygments.styles.dracula import background

from core.config import GOOGLE_API
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from database.session import get_db
from crud.msp_chat import *
from service.prompt import preview_prompt

chat_router = APIRouter(tags=["msp_chat"], prefix="/MSP_CHAT")

@chat_router.post("/msp_read_chat_session_by_user")
async def msp_read_chat_session_by_user(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")
    sessions = get_sessions_by_user(db,user_id)
    return{
        "status": True,
        "sessions":sessions
    }

@chat_router.post("/msp_read_message_by_session")
async def msp_read_message_by_session(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    session_id = body.get("session_id")
    messages = get_messages_by_session(db,session_id)
    return{
        "status": True,
        "messages":messages
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
    project_id = body.get("project_id ")

    if session_id == 0 :
        result = preview_prompt(user_input)
        preview = result.get("preview")
        title = result.get("title")

        new_session = create_session(
            db=db,
            user_id=user_id,
            title=title,
            # project_id=project_id,
            preview=preview
        )

        session_id = new_session.id


    # 1. 사용자 메시지 저장 (즉시 저장)
    user_message = create_message(db, session_id=session_id, role=role, content=user_input)

    # 2. LLM 호출
    google_assistant = ChatGoogleGenerativeAI(model=chat_model, api_key=GOOGLE_API)
    result = google_assistant.invoke(user_input)

    # 3. AI 응답 저장 (백그라운드로 저장 가능)
    background_tasks.add_task(
        create_message,
        db,
        session_id=session_id,
        role="assistant",
        content=result.content
    )

    return{
        "status": "success",
        "user_message_id": user_message.id,
        "response": result.content,
        "session_id":session_id
    }