from fastapi import APIRouter, Depends, status, HTTPException
from database.session import get_db
from fastapi.responses import JSONResponse
from fastapi import Request
from crud.llm import *
from schemas.llm import *
from langchain_service.chains.file_chain import get_file_chain
from langchain_service.chains.qa_chain import qa_chain, process_usage_in_background, get_session_title
from langchain_service.agents.file_agent import get_file_agent
from langchain_service.embeddings.get_vector import text_to_vector
from langchain_service.chains.image_generator import *
import core.config as config
from fastapi import BackgroundTasks
from service.sms.make_code import generate_verification_code
import os

langchain_router = APIRouter()

@langchain_router.post("/UploadFile", response_model=FileUploadResponse)
async def upload_file_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
        form_data = await request.form()
        project_id = form_data.get("project_id")
        project_id = int(project_id) if project_id is not None else None
        user_email = form_data.get("user_email")
        session_id = form_data.get("session_id")
        files = form_data.getlist("files[]")
        save_dir = config.UPLOAD_FOLDER
        user_dir = os.path.join(save_dir, user_email, 'document')
        os.makedirs(user_dir, exist_ok=True)
        print(f"파일1 ")
        origin_name, file_name, file_path = "", "", ""
        for file in files:
            origin_name = file.filename
            random_number = generate_verification_code()
            file_name = f"{project_id}_{random_number}_{file.filename}"  # 파일명에 project_id와 랜덤번호 추가
            file_path = os.path.join(user_dir, file_name)  # 사용자 폴더에 저장할 경로

            with open(file_path, "wb") as f:
                content = await file.read()  # 파일 내용 읽기
                f.write(content)  # 파일 내용 저장

        file_id = upload_file(db=db, project = project_id, email=user_email, url=file_path, name=origin_name)
        file_content = get_file_chain(db=db, id = file_id, file_path=file_path)
        print(f"파일 체인 {file_content}")

        agent = get_file_agent(file_content)
        summary = agent()
        print(f"요약 : \n{summary}")

        message1 = f"파일 업로드 : {file_name}"
        message2 = summary
        vector1 = text_to_vector(message1)
        vector2 = text_to_vector(message2)
        add_message(db = db, session_id = session_id, project_id = project_id, user_email=user_email, message_role='user', conversation=message1, vector_memory=vector1)
        add_message(db=db, session_id = session_id, project_id = project_id, user_email=user_email, message_role='assistant', conversation=message2, vector_memory=vector2)
        return JSONResponse(content={"message": summary})
    except Exception:
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류 발생")

'''
@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    session = request.session
    model = request.selected_model
    if model in config.OPENAI_MODELS:
        provider = "openai"
    elif model in config.ANTHROPIC_MODELS:
        provider = "anthropic"
    else:
        return "해당 모델은 아직 지원되지 않는 모델입니다.\n다른 모델을 선택해주세요."
    api_key = get_api_key(db=db, user_email=email, provider=provider)
    if not api_key:
        return "보유 중인 API키가 없습니다.\n우선 API키를 등록해주세요."
    try :
        response_text, vector, formatted_history = qa_chain(
            db = db, session_id=session, conversation=message, provider=provider, model=model, api_key=api_key
        )
        background_tasks.add_task(
            get_session_title,
            db, session, message
        )
        background_tasks.add_task(
            process_usage_in_background,
            db, session, project_id, email, provider, model,
            message, response_text, formatted_history, vector
        )

        print("✅ 응답을 넘겼습니다.")
        return response_text
    except Exception as e:
        print(f"Error Occured f{e}")
        return "현재 등록하신 API 키는 유효하지 않습니다.\n유효하는 API키를 등록해주세요."
'''


@langchain_router.post("/modelsList", response_model=ModelListResponse)
async def model_list(db: Session = Depends(get_db)):
    models_list = get_model_list(db)
    return models_list

@langchain_router.post("/DeleteModel", response_model=DeleteModelResponse)
async def model_delete(request : DeleteModelRequest, db: Session = Depends(get_db)):
    model_id = request.id
    delete_model(db, model_id=model_id)
    return JSONResponse(content={"message": "모델 삭제 성공"})

@langchain_router.post("/DeleteProvider", response_model=DeleteProviderResponse)
async def provider_delete_endpoint(request : DeleteProviderRequest, db: Session = Depends(get_db)):
    provider_id = request.id
    delete_provider(db, provider_id=provider_id)
    return JSONResponse(content={"message": "Provider 삭제 성공"})

@langchain_router.post("/AddNewProvider", response_model=AddNewProviderResponse)
async def new_provider_endpoint(request : AddNewProviderRequest, db: Session = Depends(get_db)):
    name = request.name
    model_status = request.status
    website = request.website
    description = request.description
    add_provider(db = db, name = name, status = model_status, website = website, description = description )
    return JSONResponse(content={"message": "Provider 추가 성공"})

@langchain_router.post("/AddNewModel", response_model = AddModelResponse)
async def new_model_endpoint(request : AddModelRequest, db: Session = Depends(get_db)):
    provider_name = request.provider_name
    name = request.name
    add_model(db=db, provider_name = provider_name, name = name)
    return JSONResponse(content={"message": "모델 추가 성공"})

@langchain_router.post("/ChangeModel", response_model=ChangeModelResponse)
async def change_model_endpoint(request : ChangeModelRequest, db: Session = Depends(get_db)):
    before_id = request.model_before.id
    provider_name = request.model_new.provider_name
    name = request.model_new.name
    change_model(db = db, id = before_id, provider_name = provider_name, name=name)
    return JSONResponse(content={"message": "모델 수정 성공"})

@langchain_router.post("/APIkeyList")
async def api_list_endpoint(request : GetSessionRequest, db: Session = Depends(get_db)):
    email = request.email
    api_key_list = get_api_keys(db,email)
    return api_key_list

@langchain_router.post("/getSessions")
async def get_session_endpoint(request: GetSessionRequest, db: Session = Depends(get_db)):
    try:
        email = request.email
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        response = get_session(db, email)
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No sessions found for email: {email}"
            )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@langchain_router.post("/getConversations", response_model=GetConversationResponse)
async def get_conversation_endpoint(request: GetConversationRequest, db: Session = Depends(get_db)):
    try:
        email = request.email
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        response = get_conversation(db, email)
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No sessions found for email: {email}"
            )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@langchain_router.post("/newSession", response_model=NewSessionResponse)
async def new_session_endpoint(request : NewSessionRequest, db: Session = Depends(get_db)):
    session_id = request.id
    session_title = request.session_title
    project_id = request.project_id
    user_email = request.user_email
    response = add_new_session(db=db, id = session_id, project_id=project_id, session_title=session_title, user_email=user_email)
    if response == "already_exist":
        return JSONResponse(content={"message": "요청이 너무 빈번합니다."})
    return response


@langchain_router.post("/getInfoBase")
async def get_infobase_endpoint(request : GetInfoBaseRequest, db: Session = Depends(get_db)):
    project = request.activeProject
    email = project.user_email
    project_id = project.project_id

    infobase = get_infobase(db,email,project_id)

    return infobase


@langchain_router.post("/changeProviderStatus", response_model = ProviderStatusResponse)
async def change_provider_status_endpoint(request : ProviderStatusRequest, db : Session = Depends(get_db)):
    provider_id = request.provider_id
    try:
        change_provider_status(db = db, provider_id = provider_id)
        return JSONResponse(content={"message" : "Provider Status 전환 성공"})
    except Exception as e:
        print(f"Provider Status 전환 에러 : {e}")
        return JSONResponse(content={"message" : "Provider Status 전환 실패"})


@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    session = request.session
    model = request.selected_model

    if model in config.OPENAI_MODELS:
        provider = "openai"
    elif model in config.ANTHROPIC_MODELS:
        provider = "anthropic"
    else:
        return "해당 모델은 아직 지원되지 않는 모델입니다.\n다른 모델을 선택해주세요."
    api_key = get_api_key(db=db, user_email=email, provider=provider)

    translate_prompt = discrimination(message)

    if translate_prompt == 2:
        translate_english = translateToenglish(message)
        print(translate_english)

        response_url = generate_image_with_openai(translate_english, "dall-e-3")
        print("=========================================================================================")
        print(response_url)
        vector = text_to_vector(message)
        vector2 = text_to_vector(response_url)
        add_message(db=db, session_id=session, project_id=project_id, user_email=email,
                    message_role='user', conversation=message, vector_memory=vector)

        add_message(db=db, session_id=session, project_id=project_id, user_email=email,
                    message_role='assistant', conversation=response_url, vector_memory=vector2)
        return response_url
    elif translate_prompt == 3:
        return "현재 비디오 생성은 지원되지 않습니다."
    elif translate_prompt == 4:
        return "현재 데이터(표, 차트, 그래프, 기타 데이터 시각화) 생성은 지원되지 않습니다."
    elif translate_prompt == 5:
        return "현재 오디오 생성은 지원되지 않습니다."

    if not api_key:
        return "보유 중인 API키가 없습니다.\n우선 API키를 등록해주세요."
    try :
        response_text, vector, formatted_history = qa_chain(
            db = db, session_id=session, conversation=message, provider=provider, model=model, api_key=api_key
        )
        background_tasks.add_task(
            get_session_title,
            db, session, message
        )
        background_tasks.add_task(
            process_usage_in_background,
            db, session, project_id, email, provider, model,
            message, response_text, formatted_history, vector
        )

        print("✅ 응답을 넘겼습니다.")
        return response_text
    except Exception as e:
        print(f"Error Occured f{e}")
        return "현재 등록하신 API 키는 유효하지 않습니다.\n유효하는 API키를 등록해주세요."