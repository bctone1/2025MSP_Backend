# LANGCHAIN_SERVICE/Chain/pdf_chain.py
from pathlib import Path
from glob import glob
import uuid
from langchain_service.memory.relevant_message import get_relevant_messages
from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from core.config import OPENAI_API, EMBEDDING_API
from langchain_core.output_parsers import StrOutputParser
import numpy as np
from sqlalchemy.orm import Session
from langchain.prompts import PromptTemplate
from langchain_service.llm.setup import get_llm

# async def pdfRAG(files: list[UploadFile], question: str) -> str:
#     """
#     여러 개의 PDF 파일을 업로드 받아 RAG 수행 후 답변 반환
#     """
#     # 업로드 파일 저장 디렉토리
#     tmp_dir = Path("FILE/Upload")
#     tmp_dir.mkdir(parents=True, exist_ok=True)
#
#     # 업로드된 파일 저장
#     for file in files:
#         tmp_path = tmp_dir / f"{uuid.uuid4()}_{file.filename}"
#         with open(tmp_path, "wb") as out:
#             out.write(await file.read())
#
#     # 여러 PDF 처리
#     file_paths = glob("FILE/Upload/*.pdf")
#     if not file_paths:
#         raise HTTPException(status_code=400, detail="No PDF files found.")
#
#     # 문서 로드
#     documents = []
#     for path in file_paths:
#         documents.extend(PyMuPDFLoader(path).load())
#
#     # 문서 분할
#     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
#     split_docs = splitter.split_documents(documents)
#
#     # 벡터스토어 생성
#     embeddings = OpenAIEmbeddings(api_key=EMBEDDING_API)
#     vectorstore = FAISS.from_documents(split_docs, embeddings)
#     retriever = vectorstore.as_retriever()
#
#     #    prompt = PromptTemplate.from_template(
#     #         """You are an assistant for question-answering tasks.
#     # Use the following pieces of retrieved context to answer the question.
#     # If you don't know the answer, just say that you don't know.
#     # Answer in Korean.
#
#
#     # LLM
#     llm = ChatOpenAI(model_name="gpt-4o", api_key=OPENAI_API, temperature=0.0)
#
#     # QA 체인
#     qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
#     answer = qa.run(question)
#
#     return answer

################################################################################################

async def pdfRAG(
    db: Session,
    session_id: str,
    files: list[UploadFile],
    question: str,
    provider="openai",
    model="gpt-4o",
    api_key: str = None,
) -> str:
    # --------------------
    # 1. PDF 처리
    tmp_dir = Path("FILE/Upload")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    file_paths = []
    for file in files:
        tmp_path = tmp_dir / f"{uuid.uuid4()}_{file.filename}"
        with open(tmp_path, "wb") as out:
            out.write(await file.read())
        file_paths.append(tmp_path)

    documents = []
    for path in file_paths:
        documents.extend(PyMuPDFLoader(str(path)).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    split_docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.get_relevant_documents(question)

    # --------------------
    # 2. 대화 히스토리 검색
    query_vector = np.array(embeddings.embed_query(question))
    relevant_messages = get_relevant_messages(db, session_id, query_vector, top_n=5)

    # --------------------
    # 3. 프롬프트 준비
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    history = "\n".join(
        [f"{msg['message_role'].capitalize()}: {msg['conversation']}" for msg in relevant_messages]
    )

    prompt = PromptTemplate(
        input_variables=["history", "context", "input"],
        template=(
            "{history}\n\n# 문서 Context:\n{context}\n\n"
            "Human: {input}\nAI:"
        ),
    )

    llm = get_llm(provider, model, api_key=api_key)
    chain = prompt | llm | StrOutputParser()

    # --------------------
    # 4. 실행
    response_text = chain.invoke({"history": history, "context": context, "input": question})
    return response_text


#################################################################################################
#     _ = vectorstore.index.reconstruct(0)
#     n_vectors = vectorstore.index.ntotal
#     _ = np.array([vectorstore.index.reconstruct(i) for i in range(n_vectors)])
#
#     retriever = vectorstore.as_retriever()
#
#     prompt = PromptTemplate.from_template(
#         """You are an assistant for question-answering tasks.
# Use the following pieces of retrieved context to answer the question.
# If you don't know the answer, just say that you don't know.
# Answer in Korean.
# ...
#     chain = (
#         {"context": retriever | docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
