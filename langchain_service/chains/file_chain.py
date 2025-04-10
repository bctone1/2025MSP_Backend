from langchain_service.document_loaders.file_loader import load_document
from langchain_service.document_loaders.indexer import *
from langchain_service.embeddings.get_vector import text_to_vector
from sqlalchemy.orm import Session
from crud.langchain import get_embedding_key
from crud.langchain import *

def get_file_chain(db: Session, id : int, file_path: str):
    get_embedding_key(db = db)
    documents = load_document(file_path)
    index_documents(db=db, id=id, documents=documents)
    return documents

