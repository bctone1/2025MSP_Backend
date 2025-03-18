from langchain.schema import Document
from langchain_service.vector_stores.setup import get_pgvector_db
from langchain_service.embeddings.setup import get_embeddings
from langchain_service.document_loaders.indexer import index_documents

def test_split_and_index_documents():
    # 테스트용 문서 생성
    document_text = (
        "LangChain을 사용하여 문서를 분할하고 인덱싱하는 예제입니다. "
        "이 문서는 다양한 크기의 청크로 나누어져 벡터 스토어에 인덱싱됩니다."
        "각각의 청크는 임베딩을 통해 벡터화되어 저장됩니다."
    )
    documents = [Document(page_content=document_text, metadata={"source": "test_file.txt"})]

    # 문서 분할 및 벡터 스토어 인덱싱
    try:
        # 문서를 분할하고 인덱싱
        vector_db = index_documents(documents)

        # 결과 확인
        print("✅ 문서 인덱싱 성공!")
        print(f"사용된 벡터 스토어: {type(vector_db)}")

        # PGVector의 경우, 인덱싱된 문서 개수를 확인하는 대신 쿼리 방식으로 데이터를 확인할 수 있습니다.
        # 예시로 첫 번째 문서와 비슷한 문서를 찾는 방식으로 확인
        query_result = vector_db.similarity_search("LangChain을 사용한 문서", k=3)
        print(f"쿼리 결과: {query_result}")

    except Exception as e:
        print("❌ 에러 발생:", e)

if __name__ == "__main__":
    test_split_and_index_documents()