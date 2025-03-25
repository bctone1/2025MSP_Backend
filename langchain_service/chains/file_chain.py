from langchain_service.document_loaders.file_loader import load_document
from langchain_service.embeddings.get_vector import text_to_vector

def get_file_chain(file_path: str):
    documents = load_document(file_path)
    print(documents)
    texts = [doc.page_content for doc in documents]
    print(f"파일 추출 성공 : {texts}")
    vectors = [text_to_vector(text) for text in texts]
    print(f"임베딩 성공 : {vectors}")
    return vectors

