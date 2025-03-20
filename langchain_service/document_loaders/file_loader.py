from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader
)
import os

## LangChain에서 사용하는 파일 로더 사용
def load_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext in ['.docx', '.doc']:
        loader = Docx2txtLoader(file_path)
    elif ext == '.csv':
        loader = CSVLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"지원되지 않는 파일 형식: {ext}")

    return loader.load()