from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from core.tools import fit_anthropic_model
import core.config as config

def get_llm(provider="openai", model=None, api_key : str = None):
    if provider == "openai":
        model_name = model or config.DEFAULT_CHAT_MODEL
        return ChatOpenAI(
            openai_api_key = api_key,
            model_name=model_name,
            temperature=0.7
        )
    elif provider == "anthropic":
        model = fit_anthropic_model(model_name = model)
        model_name = model or "claude-3-sonnet-20240229"
        return ChatAnthropic(
            anthropic_api_key = api_key,
            model=model_name,
            temperature=0.7
        )
    else:
        raise ValueError(f"지원되지 않는 제공자: {provider}")


def get_backend_agent(provider="openai", model=None):
    if provider == "openai":
        model_name = model or config.DEFAULT_CHAT_MODEL
        return ChatOpenAI(
            openai_api_key=config.EMBEDDING_API,
            model_name=model_name,
            temperature=0.7
        )

