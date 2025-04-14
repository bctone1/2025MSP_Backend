from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_service.vector_stores.setup import get_pgvector_db
from langchain_service.embeddings.get_vector import text_to_vector
from typing import List
from langchain.schema import Document
from sqlalchemy.orm import Session
from crud.langchain import save_info

def split_documents(documents: List[Document], chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

def index_documents(db: Session, id : int, documents: List[Document], use_pgvector=True):
    chunks = split_documents(documents)
    if use_pgvector:
        vectors = [text_to_vector(chunk.page_content) for chunk in chunks]
        texts = [chunk.page_content for chunk in chunks]
    for idx, chunk in enumerate(chunks):
        content = chunk.page_content
        vector_memory = vectors[idx]

        save_info(db=db, infobase_id=id, content = content, vector_memory = vector_memory)
