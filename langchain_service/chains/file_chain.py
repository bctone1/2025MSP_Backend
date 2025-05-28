from core.config import DOCUMENT_EXTENSION
from langchain_service.document_loaders.file_loader import load_document
from langchain_service.document_loaders.indexer import *
from pathlib import Path


def get_file_chain(db: Session, id : int, file_path: str):
    document_extension = DOCUMENT_EXTENSION
    ext = Path(file_path).suffix.lower()

    if ext in document_extension:
        documents = load_document(file_path)
        index_documents(db=db, id=id, documents=documents)
        return documents[0].page_content