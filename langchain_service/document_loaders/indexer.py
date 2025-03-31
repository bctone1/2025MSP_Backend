from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_service.vector_stores.setup import get_pgvector_db
from langchain_service.embeddings.get_vector import text_to_vector
from typing import List
from langchain.schema import Document
from sqlalchemy.orm import Session
from crud.langchain import save_info

def split_documents(documents: List[Document], chunk_size=1000, chunk_overlap=200):
    """
    문서를 청크로 분할합니다.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

'''
def index_documents(documents: List[Document], collection_name="documents", use_pgvector=True):
    """
    문서를 분할하고 벡터 스토어에 인덱싱합니다.
    """
    chunks = split_documents(documents)

    if use_pgvector:
        vector_db = get_pgvector_db(collection_name)
    else:
        from langchain_service.vector_stores.setup import get_chroma_db
        vector_db = get_chroma_db(collection_name)

    vector_db.add_documents(chunks)
    return vector_db

'''

def index_documents(db: Session, id : int, documents: List[Document], use_pgvector=True):
    chunks = split_documents(documents)
    if use_pgvector:
        vectors = [text_to_vector(chunk.page_content) for chunk in chunks]
        texts = [chunk.page_content for chunk in chunks]
    for idx, chunk in enumerate(chunks):
        content = chunk.page_content
        vector_memory = vectors[idx]

        save_info(db=db, infobase_id=id, content = content, vector_memory = vector_memory)

    print("✅All documents indexed and saved.")