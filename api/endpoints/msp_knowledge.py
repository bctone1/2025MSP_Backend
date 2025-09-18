from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from service.prompt import pdf_preview_prompt, preview_prompt

from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_service.document_loader.indexer import KssTextSplitter
from schemas.msp_project import InvokeRequest
from service.prompt import pdf_preview_prompt
from service.sms.generate_random_code import generate_verification_code
from crud.msp_knowledge import *
import core.config as config
import os, json
from database.session import get_db
from crud.msp_chat import create_session
from fastapi.responses import FileResponse

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains import RetrievalQA

from langchain_community.chat_models import ChatOpenAI

from langchain_service.embedding.get_vector import text_to_vector
from models import MSP_Knowledge
from sqlalchemy.orm import Session
from models.knowledge import MSP_KnowledgeChunk

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
async def msp_get_knowledge_by_user(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")
    knowledges = get_knowledge_by_user(db, user_id)
    print(knowledges)
    return {
        "status": True,
        "knowledges": knowledges
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
    user_dir = os.path.join(save_dir, user_id, 'document')    # 사용자별 디렉토리
    os.makedirs(user_dir, exist_ok=True)

    # 파일 저장
    origin_name = file.filename    # 원본 파일명
    random_number = generate_verification_code()
    file_name = f"{user_id}_{random_number}_{origin_name}"

    # 저장경로 완성
    file_path = os.path.join(user_dir, file_name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    file_type = file.content_type
    file_size = len(content)

    # PDF 내용을 요약하거나 태그/미리보기를 뽑아내는 함수
    pdf_preview = pdf_preview_prompt(file_path)
    # if pdf_preview.startswith("```json"):
    #     pdf_preview = pdf_preview.replace("```json", "").replace("```", "").strip()
    # pdf_preview = json.loads(pdf_preview)

    tags = pdf_preview.get("tags", "")
    preview = pdf_preview.get("preview", [])

    # 업로드한 파일의 메타데이터를 DB의 knowledge 테이블에 기록.
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

    # 임베딩 과정 (추후 조정 가능)
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    splitter =RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # KssTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(documents)
    chunk_payload = []
    for idx, doc in enumerate(split_docs):
        vector = text_to_vector(doc.page_content)
        if vector is None:
            continue
        chunk_payload.append({"index": idx, "text": doc.page_content, "vector": vector})
    # 지식 청크 테이블에 vector 메모리에 저장
    if chunk_payload:
        create_knowledge_chunks(db, upload_result.id, chunk_payload)


    return {
        "filename": file.filename,
        "response": upload_result
    }



@knowledge_router.get("/msp_get_file")
async def msp_get_file(file_id: int, user_id: int, db: Session = Depends(get_db)):
    file_path = get_knowledge_by_id(db, file_id, user_id)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

    return FileResponse(path=file_path, filename=os.path.basename(file_path))

# vector 불러오는 테스트용
@knowledge_router.get("/msp_get_chunk_vector/{chunk_id}")
async def msp_get_chunk_vector(chunk_id: int, db: Session = Depends(get_db)):
    """
    지정한 청크의 vector_memory를 반환 확인용 test version
    """
    chunk = get_chunk_by_id(db, chunk_id)
    vector = list(chunk.vector_memory) if chunk.vector_memory is not None else None
    return {
        "status": True,
        "chunk_id": chunk.id,
        "vector": vector
    }


# 질문을 임베딩 뒤 DB에 저장된 벡터와 비교해 관련 내용을 추출하고 LLM에 전달해 답변을 생성하는 방식
@knowledge_router.post("/invoke")
async def invoke_knowledge(req: InvokeRequest , db: Session = Depends(get_db)):
    question = req.question
    user_id = req.user_id
    provider = req.provider
    model = req.model

    if not question or not user_id:
        raise HTTPException(status_code=400, detail="question과 user_id는 필수입니다.")

    # 1) 질문 문장을 임베딩 벡터로 변환
    question_vec = text_to_vector(question)

    # 2) DB저장 문서 청크 중 유사도가 높은 순으로 조회후 LLM에 전달
    chunks = (
        db.query(MSP_KnowledgeChunk)
        .join(MSP_Knowledge, MSP_KnowledgeChunk.knowledge_id == MSP_Knowledge.id)
        .filter(MSP_Knowledge.user_id == user_id)
        .order_by(MSP_KnowledgeChunk.vector_memory.cosine_distance(question_vec))
        .limit(5)
        .all()
    )
    context = "\n".join(chunk.chunk_text for chunk in chunks)

###################################################
    # 3) LLM 호출
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

    retriever = msp_get_chunk_vector.as_retriever()

    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Answer in Korean.

    #Question: 
    {question} 
    #Context: 
    {context} 

    #Answer:"""
    )


    chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    answer = chain.invoke(question)

    return {
        "status": True,
        "response": answer,
        "history": []
    }
###################################################

