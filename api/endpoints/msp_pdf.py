# API/Endpoints/pdf.py
# 추후에 msp_rag라는 이름으로 변경 예정

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain_service.chain.pdf_chain import pdfRAG

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
        answer = await pdfRAG(files, question)
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
