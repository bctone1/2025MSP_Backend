from fastapi import APIRouter, HTTPException, Depends, status
from database.session import get_db
from fastapi.responses import JSONResponse
from fastapi import Request
from crud.langchain import *
from schemas.langchain import *
from langchain_service.chains.file_chain import get_file_chain
from langchain_service.chains.qa_chain import qa_chain
from langchain_service.agents.session_agent import get_session_agent
from langchain_service.embeddings.get_vector import text_to_vector
import core.config as config
from fastapi import UploadFile, File, Form
import os

langchain_router = APIRouter()

@langchain_router.post("/UploadFile", response_model=FileUploadResponse)
async def upload_file(request: Request, db: Session = Depends(get_db)):
    try:
        form_data = await request.form()
        project_id = form_data.get("project_id")
        project_id = int(project_id) if project_id is not None else None
        user_email = form_data.get("user_email")
        session_id = form_data.get("session_id")
        files = form_data.getlist("files[]")

        save_dir = config.UPLOADED_FILES
        os.makedirs(save_dir, exist_ok=True)
        file_name, file_path = "", ""
        for file in files:
            file_name = file.filename
            file_location = os.path.join(save_dir, file.filename)
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            file_path = f"{save_dir}/{file.filename}"
        file_id = upload_file(db=db, project = project_id, email=user_email, url=file_path)
        get_file_chain(db=db, id = file_id, file_path=file_path)
        message1 = f"파일 업로드 : {file_name}"
        message2 = "파일이 지식 베이스에 추가되었습니다. 어떤 도움이 필요하신가요?"
        vector1 = text_to_vector(message1)
        vector2 = text_to_vector(message2)
        add_message(db = db, session_id = session_id, project_id = project_id, user_email=user_email, message_role='user', conversation=message1, vector_memory=vector1)
        add_message(db=db, session_id = session_id, project_id = project_id, user_email=user_email, message_role='assistant', conversation=message2, vector_memory=vector2)
        return JSONResponse(content={"message": "파일 업로드 성공"})
    except Exception:
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류 발생")


'''
@langchain_router.post("/UploadFile")
async def upload_file_debug(request: Request):
    try:
        # headers
        print("=== Headers ===")
        for k, v in request.headers.items():
            print(f"{k}: {v}")

        # content type
        print("=== Content-Type ===")
        print(request.headers.get("content-type"))

        # raw body
        body_bytes = await request.body()
        print("=== Raw Body ===")
        print(body_bytes[:500])  # 너무 길면 잘라서 보기

        # try parsing as form
        print("=== Form Fields ===")
        try:
            form = await request.form()
            for key, value in form.multi_items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"Form parsing error: {e}")

        return JSONResponse(content={"status": "debug info printed"}, status_code=200)

    except Exception as e:
        print(f"Unhandled error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
'''

@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    session = request.session
    model = request.selected_model
    first = is_this_first(db=db, session_id = session)
    if model in config.OPENAI_MODELS:
        provider = "openai"
    elif model in config.ANTHROPIC_MODELS:
        provider = "anthropic"
    else:
        return JSONResponse(content={"message": "해당 모델은 META LLM MSP에서 제공하지 않는 모델입니다."})
    get_api_key(db=db, user_email=email, provider=provider)

    if first:
        agent_executor = get_session_agent(session)
        response = agent_executor(message)
        change_session_title(db=db, session_id=session, content=response.content)
    a = qa_chain(db = db, session_id=session, project_id=project_id, user_email=email, conversation=message, provider=provider, model=model)
    return a

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