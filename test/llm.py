from langchain_service.llms.setup import get_llm
import core.config as config

'''if __name__ == "__main__":
    # OpenAI 제공자 테스트
    try:
        print("=== OpenAI 테스트 ===")
        llm_openai = get_llm(provider="openai", model="gpt-3.5-turbo")
        print("✅ OpenAI LLM 객체 생성 성공!")
        print("객체 타입:", type(llm_openai))

        # 간단한 프롬프트 실행 테스트
        openai_response = llm_openai.invoke("안녕하세요! 당신은 누구신가요?")
        print("🎯 OpenAI 응답:", openai_response)
    except Exception as e:
        print("❌ OpenAI 에러 발생:", e)

    # Anthropic 제공자 테스트
    try:
        print("\n=== Anthropic 테스트 ===")
        llm_anthropic = get_llm(provider="anthropic")
        print("✅ Anthropic LLM 객체 생성 성공!")
        print("객체 타입:", type(llm_anthropic))

        # 간단한 프롬프트 실행 테스트
        anthropic_response = llm_anthropic.invoke("안녕하세요! 당신은 누구신가요?")
        print("🎯 Anthropic 응답:", anthropic_response)
    except Exception as e:
        print("❌ Anthropic 에러 발생:", e)
'''