from langchain_openai import OpenAIEmbeddings
import core.config as config

def get_embeddings():
    return OpenAIEmbeddings(
        api_key = config.GPT_API,
        model=config.EMBEDDING_MODEL
    )

'''
if __name__ == "__main__":
    try:
        # OpenAI 임베딩 객체 생성
        embeddings = get_embeddings()
        print("✅ Embeddings 객체 생성 성공!")
        print("객체 타입:", type(embeddings))

        # 간단한 텍스트 임베딩 테스트
        test_text = "LangChain을 사용한 텍스트 임베딩 테스트입니다."
        # OpenAIEmbeddings 클래스가 제공하는 메서드(예: embed_query) 사용
        embedding_result = embeddings.embed_query(test_text)
        print("🎯 임베딩 결과:", embedding_result)
    except Exception as e:
        print("❌ 에러 발생:", e)
'''