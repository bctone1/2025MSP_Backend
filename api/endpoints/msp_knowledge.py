from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
import json
from service.prompt import pdf_preview_prompt, preview_prompt
from service.sms.generate_random_code import generate_verification_code
from crud.msp_knowledge import *
import core.config as config
import os
from database.session import get_db
from crud.msp_chat import create_session

knowledge_router = APIRouter(tags=["msp_knowledge"], prefix="/MSP_KNOWLEDGE")


@knowledge_router.post("/msp_get_session_knowledge_association")
async def msp_get_session_knowledge_association(
        request: Request,
        db: Session = Depends(get_db)
):
    body = await request.json()
    session_id = body.get("session_id")
    knowledge_ids = get_session_knowledge_association(db, session_id)
    return {
        "status": True,
        "knowledge_ids": knowledge_ids
    }


@knowledge_router.post("/msp_add_session_knowledge_association")
async def msp_add_session_knowledge_association(
        request: Request,
        db: Session = Depends(get_db)
):
    body = await request.json()
    session_id = body.get("session_id")
    knowledge_ids = body.get("knowledge_ids")

    # 세션생성 용 정보
    user_id = body.get("user_id")
    project_id = body.get("project_id")
    title = None

    if session_id == 0:
        result = preview_prompt("사용자가 새로운 대화를 시작하면서 참고 파일을 선택했습니다.")
        preview = result.get("preview")
        title = result.get("title")

        new_session = create_session(
            db=db,
            user_id=user_id,
            project_id=project_id,
            title=title,
            preview=preview
            # title="title",
            # preview="preview"
        )
        session_id = new_session.id

    if not isinstance(knowledge_ids, list):
        knowledge_ids = [knowledge_ids]  # 단일 값일 경우 리스트로 변환
    associations = add_session_knowledge_association(db, session_id, knowledge_ids)
    return {
        "status": True,
        "associations": associations,
        "session_id": session_id,
        "title": title
    }


@knowledge_router.post("/msp_get_knowledge_by_user")
async def msp_get_knowledge_by_user(
        request: Request,
        db: Session = Depends(get_db)
):
    body = await request.json()
    user_id = body.get("user_id")
    knowledges = get_knowledge_by_user(db, user_id)
    print(knowledges)
    return {
        "status": True,
        "kbowledges": knowledges
    }


# Rag 파일업로드 요청
@knowledge_router.post("/msp_upload_file")
async def msp_upload_file(
        request: Request,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    form_data = await request.form()
    user_id = form_data.get("user_id")
    save_dir = config.UPLOAD_FOLDER
    user_dir = os.path.join(save_dir, user_id, 'document')
    os.makedirs(user_dir, exist_ok=True)

    # 파일 저장
    origin_name = file.filename
    random_number = generate_verification_code()
    file_name = f"{user_id}_{random_number}_{origin_name}"
    file_path = os.path.join(user_dir, file_name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    file_type = file.content_type
    file_size = len(content)

    pdf_preview = pdf_preview_prompt(file_path)
    # if pdf_preview.startswith("```json"):
    #     pdf_preview = pdf_preview.replace("```json", "").replace("```", "").strip()
    # pdf_preview = json.loads(pdf_preview)

    tags = pdf_preview.get("tags", "")
    preview = pdf_preview.get("preview", [])

    upload_result = create_knowledge(db,
                                     origin_name=origin_name,
                                     file_path=file_path,
                                     file_type=file_type,
                                     file_size=file_size,
                                     user_id=user_id,
                                     tags=tags,
                                     preview=preview
                                     # tags=["dkdkdk","asdfasdf"],
                                     # preview="sdlhaf;kljafdjkl"
                                     )

    return {
        "filename": file.filename,
        "response": upload_result
    }
