from langchain_service.vector_stores.setup import get_chroma_db, get_pgvector_db
import core.config as config
'''
if __name__ == "__main__":
    test_texts = ["LangChain은 강력한 AI 프레임워크입니다.", "Vector DB를 사용하여 검색을 향상할 수 있습니다."]

    # 🔹 Chroma DB 테스트
    try:
        print("=== Chroma DB 테스트 ===")
        chroma_db = get_chroma_db(collection_name="test_collection")
        print("✅ Chroma DB 객체 생성 성공!")
        print("객체 타입:", type(chroma_db))

        # Chroma에 샘플 데이터 추가
        chroma_db.add_texts(test_texts)
        print("🎯 Chroma DB 데이터 추가 성공!")
    except Exception as e:
        print("❌ Chroma DB 에러 발생:", e)

    # 🔹 PGVector 테스트
    try:
        print("\n=== PGVector 테스트 ===")
        pgvector_db = get_pgvector_db(collection_name="test_collection")
        print("✅ PGVector 객체 생성 성공!")
        print("객체 타입:", type(pgvector_db))

        # PGVector에 샘플 데이터 추가
        pgvector_db.add_texts(test_texts)
        print("🎯 PGVector DB 데이터 추가 성공!")
    except Exception as e:
        print("❌ PGVector 에러 발생:", e)
'''