from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import core.config as config

def get_llm(provider="openai", model=None):
    """
    지정된 제공자와 모델에 따라 LLM 인스턴스를 반환합니다.
    """
    if provider == "openai":
        model_name = model or config.DEFAULT_CHAT_MODEL
        return ChatOpenAI(
            api_key=config.GPT_API,
            model_name=model_name,
            temperature=0.7
        )
    elif provider == "anthropic":
        model_name = model or "claude-3-sonnet-20240229"
        return ChatAnthropic(
            api_key=config.CLAUDE_API,
            model=model_name,
            temperature=0.7
        )
    else:
        raise ValueError(f"지원되지 않는 제공자: {provider}")