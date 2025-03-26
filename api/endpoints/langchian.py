from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from database.session import get_db_connection, get_db
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from typing import List, Annotated
from crud.langchain import *
from schemas.langchain import *
from langchain_service.chains.file_chain import get_file_chain
from langchain_service.chains.qa_chain import qa_chain
from langchain_service.llms.setup import get_llm
import core.config as config
import os

langchain_router = APIRouter()

@langchain_router.post("/UploadFile", response_model=FileUploadRequest)
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
        vector = get_file_chain(file_path=file_path)
        print(vector)
        upload_file(db=db, project=10, email='user1@example.com', url=file_path, vector=vector)
        return JSONResponse(content={"message": "파일 업로드 성공", "file_count": len(files)})
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
    email = 'user2@example.com'
    project_id = 11
    message = request.messageInput
    a = qa_chain(db = db, session_id=1, project_id=project_id, user_email=email, conversation=message)
    print(a)
    return message