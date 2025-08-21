from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from database.session import get_db
from crud.llm import *
from schemas.llm import *
from langchain_service.chain.file_chain import get_file_chain
from langchain_service.chain.qa_chain import qa_chain, process_usage_in_background, get_session_title
from langchain_service.prompt.file_agent import get_file_agent
from langchain_service.embedding.get_vector import text_to_vector
from langchain_service.chain.image_generator import *
from langchain_service.vision.download_image import save_image_from_url
from langchain_service.agent.code_agent import code_agent
from service.sms.generate_random_code import generate_verification_code
from core.config import EMBEDDING_API, FRIENDLI_API, CLAUDE_API, OPENAI_API
import core.config as config
import os


langchain_router = APIRouter(tags=["LLM"], prefix="/LLM")
# langchain_router = APIRouter()

# =======================================
# 파일 업로드 → 요약/벡터화 → DB 저장
# =======================================
@langchain_router.post("/UploadFile")
async def upload_file_endpoint(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        form_data = await request.form()
        project_id = form_data.get("project_id")
        project_id = int(project_id) if project_id is not None else None
        user_email = form_data.get("user_email")
        session_id = form_data.get("session_id")

        # 저장 경로 생성
        save_dir = config.UPLOAD_FOLDER
        user_dir = os.path.join(save_dir, user_email, 'document')
        os.makedirs(user_dir, exist_ok=True)

        # 파일 저장
        origin_name = file.filename
        random_number = generate_verification_code()
        file_name = f"{project_id}_{random_number}_{origin_name}"
        file_path = os.path.join(user_dir, file_name)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # DB에 업로드 정보 저장
        file_id = upload_file(db=db, project=project_id, email=user_email, url=file_path, name=origin_name)
        file_content = get_file_chain(db=db, id=file_id, file_path=file_path)

        # 파일 요약 생성
        agent = get_file_agent(file_content)
        summary = agent()

        # 대화 로그에 추가 (user + file uploader)
        message1 = f"파일 업로드 : {file_name}"
        message2 = summary
        vector1 = text_to_vector(message1)
        vector2 = text_to_vector(message2)
        add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                    message_role='user', conversation=message1, vector_memory=vector1, case="")
        add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                    message_role='file uploader', conversation=message2, vector_memory=vector2, case="")
        return JSONResponse(content={"message": summary})
    except Exception:
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류 발생")


# =======================================
# MODEL/PROVIDER CRUD
# =======================================
@langchain_router.post("/modelsList", response_model=ModelListResponse)
async def model_list(db: Session = Depends(get_db)):
    return get_model_list(db)

@langchain_router.post("/DeleteModel", response_model=DeleteModelResponse)
async def model_delete(request: DeleteModelRequest, db: Session = Depends(get_db)):
    delete_model(db, model_id=request.id)
    return JSONResponse(content={"message": "모델 삭제 성공"})

@langchain_router.post("/DeleteProvider", response_model=DeleteProviderResponse)
async def provider_delete_endpoint(request: DeleteProviderRequest, db: Session = Depends(get_db)):
    delete_provider(db, provider_id=request.id)
    return JSONResponse(content={"message": "Provider 삭제 성공"})

@langchain_router.post("/AddNewProvider", response_model=AddNewProviderResponse)
async def new_provider_endpoint(request: AddNewProviderRequest, db: Session = Depends(get_db)):
    add_provider(db=db, name=request.name, status=request.status,
                 website=request.website, description=request.description)
    return JSONResponse(content={"message": "Provider 추가 성공"})

@langchain_router.post("/AddNewModel", response_model=AddModelResponse)
async def new_model_endpoint(request: AddModelRequest, db: Session = Depends(get_db)):
    add_model(db=db, provider_name=request.provider_name, name=request.name)
    return JSONResponse(content={"message": "모델 추가 성공"})

@langchain_router.post("/ChangeModel", response_model=ChangeModelResponse)
async def change_model_endpoint(request: ChangeModelRequest, db: Session = Depends(get_db)):
    change_model(db=db, id=request.model_before.id,
                 provider_name=request.model_new.provider_name,
                 name=request.model_new.name)
    return JSONResponse(content={"message": "모델 수정 성공"})


# =======================================
# API Key 리스트
# =======================================
@langchain_router.post("/APIkeyList")
async def api_list_endpoint(request: GetSessionRequest, db: Session = Depends(get_db)):
    return get_api_keys(db, request.email)


# =======================================
# 세션/대화 조회 및 생성
# =======================================
@langchain_router.post("/getSessions")
async def get_session_endpoint(request: GetSessionRequest, db: Session = Depends(get_db)):
    email = request.email
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
    response = get_session(db, email)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No sessions found for email: {email}")
    return response

@langchain_router.post("/getConversations", response_model=GetConversationResponse)
async def get_conversation_endpoint(request: GetConversationRequest, db: Session = Depends(get_db),
                                    get_conversation=None):
    email = request.email
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
    response = get_conversation(db, email)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No sessions found for email: {email}")
    return response

@langchain_router.post("/newSession", response_model=NewSessionResponse)
async def new_session_endpoint(request: NewSessionRequest, db: Session = Depends(get_db)):
    prevent = prevent_new_session(db=db, project_id=request.project_id)
    if prevent:
        return prevent
    response = add_new_session(db=db, id=request.id, project_id=request.project_id,
                               session_title=request.session_title, user_email=request.user_email)
    if response == "already_exist":
        return JSONResponse(content={"message": "요청이 너무 빈번합니다."})
    return response


# =======================================
# InfoBase 조회
# =======================================
@langchain_router.post("/getInfoBase")
async def get_infobase_endpoint(request: GetInfoBaseRequest, db: Session = Depends(get_db), get_infobase=None):
    return get_infobase(db, request.activeProject.user_email, request.activeProject.project_id)


# =======================================
# Provider Status 토글
# =======================================
@langchain_router.post("/changeProviderStatus", response_model=ProviderStatusResponse)
async def change_provider_status_endpoint(request: ProviderStatusRequest, db: Session = Depends(get_db),
                                          change_provider_status=None):
    try:
        change_provider_status(db=db, provider_id=request.provider_id)
        return JSONResponse(content={"message": "Provider Status 전환 성공"})
    except Exception as e:
        print(f"Provider Status 전환 에러 : {e}")
        return JSONResponse(content={"message": "Provider Status 전환 실패"})


# =======================================
# LLM 질의 (QA 체인 + 백그라운드 Usage 기록)
# =======================================
@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    session = request.session
    model = request.selected_model

    # 세션 존재 여부 확인 → 없으면 생성
    not_existing = is_not_existing(db=db, session_id=session)
    new = False
    if not_existing:
        new_session_data = add_new_session(db=db, id=session, project_id=project_id,
                                           session_title="New Chat!", user_email=email)
        new = True
        get_session_title(db=db, session_id=session, message=message)

    # 모델 종류 판별
    if model in config.OPENAI_MODELS:
        provider = "openai"
    elif model in config.ANTHROPIC_MODELS:
        provider = "anthropic"
    else:
        return {"response": "해당 모델은 아직 지원되지 않습니다.\n다른 모델을 선택해주세요."}

    api_key = get_api_key(db=db, user_email=email, provider=provider)
    if not api_key:
        return {"response": "보유 중인 API키가 없습니다.\n우선 API키를 등록해주세요."}

    # 메시지 타입 판별 (이미지/비디오/오디오/에이전트 등)
    translate_prompt = discrimination(message)
    if translate_prompt == 2:
        # 이미지 생성 처리
        translate_english = translateToenglish(message)
        response_url = generate_image_with_openai(translate_english, "dall-e-3")
        vector1 = text_to_vector(message)
        vector2 = text_to_vector(response_url)
        image_path = save_image_from_url(response_url, email)
        add_message(db=db, session_id=session, project_id=project_id, user_email=email,
                    message_role='user', conversation=message, vector_memory=vector1, case="")
        add_message(db=db, session_id=session, project_id=project_id, user_email=email,
                    message_role=model, conversation=image_path, vector_memory=vector2, case="image")
        return {"response": response_url, "case": "image"}
    elif translate_prompt in (3, 4):
        return {"response": "현재 비디오/오디오 생성은 지원되지 않습니다."}
    elif translate_prompt == 5:
        return {"response": "리서치 에이전트"}
    elif translate_prompt == 6:
        return {"response": "코딩 에이전트"}
    elif translate_prompt == 7:
        return {"response": "분석 에이전트"}
    elif translate_prompt == 8:
        return {"response": "문서 에이전트"}

    # 일반 QA 체인 호출
    try:
        response_text, vector, formatted_history = qa_chain(
            db=db, session_id=session, conversation=message,
            provider=provider, model=model, api_key=api_key
        )
        # 사용량 기록 백그라운드 처리
        background_tasks.add_task(
            process_usage_in_background,
            db, session, project_id, email, provider, model,
            message, response_text, formatted_history, vector
        )
        if not new:
            return {"response": response_text}
        else:
            return {
                "response": response_text,
                "session_id": new_session_data.id,
                "project_id": new_session_data.project,
                "title": new_session_data.session_title,
                "email": new_session_data.user_email,
                "register_at": new_session_data.register_at,
            }
    except Exception as e:
        print(f"Error Occured {e}")
        return "현재 등록하신 API 키는 유효하지 않습니다.\n유효한 API키를 등록해주세요."


# =======================================
# CodeAgent 테스트
# =======================================
@langchain_router.post('/CodeAgentTest')
async def agent_test(request: TestRequest, db: Session = Depends(get_db)):
    result = code_agent(db=db, user_email=request.user_email,
                        provider="openai", model="gpt-4o",
                        api_key=EMBEDDING_API, message=request.message)
    print(result)
    return result

###### 20205-08-19 #######

@langchain_router.post('/RequestMessage2')
async def request_message2(request: RequestMessageRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message: str = request.messageInput
    session = request.session
    model = request.selected_model
    print(f"사용중인 모델 : {model}")

    if model in config.OPENAI_MODELS:
        provider, api_key = "openai", config.OPENAI_API
    elif model in config.ANTHROPIC_MODELS:
        provider, api_key = "anthropic", config.CLAUDE_API
    elif model in config.GOOGLE_MODELS:
        provider, api_key = "google", config.GOOGLE_API
    elif model in config.FRIENDLI_MODELS:
        provider, api_key = "friendli", config.FRIENDLI_API
    else:
        return {"response": "해당 모델은 아직 지원되지 않습니다.\n다른 모델을 선택해주세요."}



    if not api_key:
        raise HTTPException(400, f"{provider} API 키가 없습니다.")

    llm = get_llm(provider = provider, model=model, api_key=api_key)
    try:
        ai_message = await llm.ainvoke(message)
        return {"response": ai_message.content}
    except Exception as e:
        raise HTTPException(502, f"{provider} 호출 실패: {e.__class__.__name__}: {e}")