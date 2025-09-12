# LANGCHAIN_SERVICE/Chain/pdf_chain.py
from pathlib import Path
from glob import glob
import uuid

from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from core.config import OPENAI_API, EMBEDDING_API


async def pdfRAG(files: list[UploadFile], question: str) -> str:
    """
    여러 개의 PDF 파일을 업로드 받아 RAG 수행 후 답변 반환
    """
    # 업로드 파일 저장 디렉토리
    tmp_dir = Path("FILE/Upload")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # # 업로드된 파일 저장
    # for file in files:
    #     tmp_path = tmp_dir / f"{uuid.uuid4()}_{file.filename}"
    #     with open(tmp_path, "wb") as out:
    #         out.write(await file.read())

    # 여러 PDF 처리
    file_paths = glob("FILE/Upload/*.pdf")
    if not file_paths:
        raise HTTPException(status_code=400, detail="No PDF files found.")

    # 문서 로드
    documents = []
    for path in file_paths:
        documents.extend(PyMuPDFLoader(path).load())

    # 문서 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    split_docs = splitter.split_documents(documents)

    # 벡터스토어 생성
    embeddings = OpenAIEmbeddings(api_key=EMBEDDING_API)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    retriever = vectorstore.as_retriever()

    # LLM
    llm = ChatOpenAI(model_name="gpt-4o", api_key=OPENAI_API, temperature=0.1)

    # QA 체인
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    answer = qa.run(question)

    return answer


# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_community.vectorstores import FAISS
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from dotenv import load_dotenv
# import numpy as np
# import faiss
#
# load_dotenv(override=True)
#
#
# def pdfRAG(file_path: str, question: str | None = None) -> str:
#     """Load a PDF file and answer a question about its content."""
#     loader = PyMuPDFLoader(file_path)
#     docs = loader.load()
#
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#     split_documents = text_splitter.split_documents(docs)
#
#     embeddings = OpenAIEmbeddings()
#     vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
#
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
#
# #Question:
# {question}
# #Context:
# {context}
#
# #Answer:"""
#     )
#
#     llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
#
#     chain = (
#         {"context": retriever | docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#
#     response = chain.invoke(question)
#     return response
