# API/Endpoints/pdf.py
from core.config import OPENAI_API, EMBEDDING_API
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
from glob import glob
import uuid

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA


pdf_router = APIRouter(tags=["msp_pdf"], prefix="/MSP_PDF")


@pdf_router.post("/pdfRAG")
async def pdf_rag(
    question: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """
    PDF 기반 RAG 테스트 엔드포인트 (다중 업로드 지원)
    """
    try:
        # 업로드 파일 저장 디렉토리
        tmp_dir = Path("FILE/Upload")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # 업로드된 모든 파일 저장
        for file in files:
            tmp_path = tmp_dir / f"{uuid.uuid4()}_{file.filename}"
            with open(tmp_path, "wb") as out:
                out.write(await file.read())

        # 여러 PDF 처리 (Upload 디렉토리 기준)
        file_paths = glob("FILE/Upload/*.pdf")
        if not file_paths:
            raise HTTPException(status_code=400, detail="No PDF files found.")

        # 문서 로드
        documents = []
        for path in file_paths:
            documents.extend(PyMuPDFLoader(path).load())

        # 문서 분할
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_docs = splitter.split_documents(documents)

        # 벡터스토어 생성
        embeddings = OpenAIEmbeddings(api_key=EMBEDDING_API)
        vectorstore = FAISS.from_documents(split_docs, embeddings)
        retriever = vectorstore.as_retriever()

        # LLM
        llm = ChatOpenAI(model_name="gpt-4o", api_key=OPENAI_API, temperature=0)

        # QA 체인
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        answer = qa.run(question)

        # 필요 시 임시 파일 삭제 가능
        # for path in file_paths:
        #     os.remove(path)

        return {"question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @pdf_router.post("/query")
# async def query_pdf(
#     file: UploadFile = File(...),
#     question: str | None = Form(None),
# ):
#     """
#     PDF 업로드 후 질문을 던지면 답변을 반환한다.
#     """
#     try:
#         # 임시 저장 경로 생성
#         temp_dir = Path("FILE/Upload")
#         temp_dir.mkdir(parents=True, exist_ok=True)
#         temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
#
#         # 파일 저장
#         with open(temp_path, "wb") as f:
#             f.write(await file.read())
#
#         # RAG 실행
#         answer = pdfRAG(str(temp_path), question)
#
#         # 처리 후 파일 삭제
#         # os.remove(temp_path)
#         return {"question": question, "answer": answer}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
