from langchain_service.document_loaders.file_loader import load_document
from langchain_service.document_loaders.indexer import *
from crud.langchain import *

def get_file_chain(db: Session, id : int, file_path: str):
    documents = load_document(file_path)
    index_documents(db=db, id=id, documents=documents)
    return documents

