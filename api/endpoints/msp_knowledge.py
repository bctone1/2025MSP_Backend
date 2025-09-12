from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
import json
from service.prompt import pdf_preview_prompt
from service.sms.generate_random_code import generate_verification_code
from crud.msp_knowledge import *
import core.config as config
import os
from database.session import get_db


knowledge_router = APIRouter(tags=["msp_knowledge"], prefix="/MSP_KNOWLEDGE")


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
    if pdf_preview.startswith("```json"):
        pdf_preview = pdf_preview.replace("```json", "").replace("```", "").strip()

    # 이제 JSON 로드
    pdf_preview = json.loads(pdf_preview)

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
