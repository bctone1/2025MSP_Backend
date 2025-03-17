from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader
)
import os


def load_document(file_path):
    """
    파일 확장자에 따라 적절한 로더를 사용하여 문서를 로드합니다.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        loader = TextLoader(file_path)
    elif ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext in ['.docx', '.doc']:
        loader = Docx2txtLoader(file_path)
    elif ext == '.csv':
        loader = CSVLoader(file_path)
    else:
        raise ValueError(f"지원되지 않는 파일 형식: {ext}")

    return loader.load()