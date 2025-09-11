# API/Endpoints/pdf.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import uuid
from core.config import OPENAI_API, EMBEDDING_API
from langchain_service.document_loader.file_loader import load_document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import tempfile
import os


# from service.pdf_rag import pdfRAG  # pdfRAG 함수가 있는 모듈로 경로 맞추기
from langchain_service.chain.pdf_chain import pdfRAG

pdf_router = APIRouter(tags=["msp_pdf"], prefix="/MSP_PDF")


@pdf_router.post("/pdfRAG")
async def pdf_rag(question: str = Form(...), file: UploadFile = File(...)
):
    """
    RAG test1
    """

    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        documents = load_document(tmp_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings(api_key=EMBEDDING_API)
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever()
        llm = ChatOpenAI(api_key=OPENAI_API)
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        answer = qa.run(question)
    finally:
        os.remove(tmp_path)

    return {"answer": answer}



@pdf_router.post("/query")
async def query_pdf(
    file: UploadFile = File(...),
    question: str | None = Form(None),
):
    """
    PDF 업로드 후 질문을 던지면 답변을 반환한다.
    """
    try:
        # 임시 저장 경로 생성
        temp_dir = Path("FILE/Upload")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

        # 파일 저장
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # RAG 실행
        answer = pdfRAG(str(temp_path), question)

        # 처리 후 파일 삭제
        # os.remove(temp_path)
        return {"question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
