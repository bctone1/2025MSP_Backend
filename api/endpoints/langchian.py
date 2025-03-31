from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, status
from database.session import get_db_connection, get_db
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import FastAPI, Request
from typing import List, Annotated
from crud.langchain import *
from schemas.langchain import *
from langchain_service.chains.file_chain import get_file_chain
from langchain_service.chains.qa_chain import qa_chain
from langchain_service.agents.session_agent import get_session_agent
from langchain_service.llms.setup import get_llm
import core.config as config
import os
import json

langchain_router = APIRouter()

@langchain_router.post("/UploadFile", response_model=FileUploadResponse)
async def UploadFile(request: Request, db: Session = Depends(get_db)):
    try:
        form_data = await request.form()
        project_id = form_data.get("project_id")
        user_email = form_data.get("user_email")
        files = form_data.getlist("files[]")

        print("받은 프로젝트 ID:", project_id)
        print("받은 이메일:", user_email)
        print("받은 파일 개수:", len(files))

        save_dir = config.UPLOADED_FILES
        os.makedirs(save_dir, exist_ok=True)
        file_path = ""
        for file in files:
            file_location = os.path.join(save_dir, file.filename)
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            print(f"파일 저장됨: {file.filename}")
            file_path = f"{save_dir}/{file.filename}"
        print(file_path)
        if os.path.exists(file_path):
            print(f"파일 {file_path} 존재합니다.")
        else:
            print(f"파일 {file_path} 존재하지 않습니다.")
        id = upload_file(db=db, project=10, email='user1@example.com', url=file_path)
        get_file_chain(db=db, id = id, file_path=file_path)
        return JSONResponse(content={"message": "파일 업로드 성공"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류 발생")

'''
@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    print(email, project_id, message)
    llm_openai = get_llm(provider="openai", model="gpt-3.5-turbo")
    openai_response = llm_openai.invoke(message)
    print(openai_response)
    return openai_response
'''

@langchain_router.post('/RequestMessage')
async def request_message(request: RequestMessageRequest, db: Session = Depends(get_db)):
    email = request.user_email
    project_id = request.project_id
    message = request.messageInput
    session = request.session
    first = is_this_first(db=db, id=session)
    if first == True:
        print("THIS IS FIRST MESSAGE")
        agent_executor = get_session_agent(session)
        response = agent_executor(message)
        print(f"Session Title : {response}")
        change_session_title(db=db, session_id=session, content=response.content)
    a = qa_chain(db = db, session_id=session, project_id=project_id, user_email=email, conversation=message)
    print(f"응답 내용 : {a}")
    return a

@langchain_router.post("/modelsList", response_model=ModelListResponse)
async def model_list(db: Session = Depends(get_db)):
    model_list = get_model_list(db)
    print(f"models : {model_list}")
    #response_text = "\n".join(json.dumps(model) for model in models)
    #response = StreamingResponse(iter([response_text]), media_type="text/plain")
    return model_list

@langchain_router.post("/DeleteModel", response_model=DeleteModelResponse)
async def model_delete(request : DeleteModelRequest, db: Session = Depends(get_db)):
    model_id = request.id
    print(model_id)
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
    status = request.status
    website = request.website
    description = request.description
    add_provider(db = db, name = name, status = status, website = website, description = description )
    return JSONResponse(content={"message": "Provider 추가 성공"})

@langchain_router.post("/AddNewModel", response_model = AddModelResponse)
async def new_model_endpoint(request : AddModelRequest, db: Session = Depends(get_db)):
    provider_name = request.provider_name
    name = request.name
    add_model(db=db, provider_name = provider_name, name = name)
    return JSONResponse(content={"message": "모델 추가 성공"})

@langchain_router.post("/ChangeModel", response_model=ChangeModelResponse)
async def change_model_endpoint(request : ChangeModelRequest, db: Session = Depends(get_db)):
    id = request.model_before.id
    provider_name = request.model_new.provider_name
    name = request.model_new.name
    change_model(db = db, id = id, provider_name = provider_name, name=name)

    return JSONResponse(content={"message": "모델 수정 성공"})

@langchain_router.post("/APIkeyList")
async def api_list_endpoint(db: Session = Depends(get_db)):
    api_key_list = get_api_keys(db)
    return api_key_list

@langchain_router.post("/getSessions")
async def get_session_endpoint(request: GetSessionRequest, db: Session = Depends(get_db)):
    try:
        email = request.email
        print(f"EMAIL : {email}" )
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        response = get_session(db, email)  # get_session 함수에서 DB 쿼리 실행
        if response is None:
            print("NO RESPONSE")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No sessions found for email: {email}"
            )

        print(f"response: {response}")
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
        print(f"EMAIL : {email}" )
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        response = get_conversation(db, email)
        if response is None:
            print("NO RESPONSE")
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
    id = request.id
    session_title = request.session_title
    project_id = request.project_id
    user_email = request.user_email
    response = add_new_session(db=db, id = id, project_id=project_id, session_title=session_title, user_email=user_email)
    print(response)
    return response