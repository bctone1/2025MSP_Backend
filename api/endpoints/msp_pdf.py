# API/Endpoints/pdf.py
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
