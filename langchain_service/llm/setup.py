from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from core.tools import fit_anthropic_model, ChatLgAI
import core.config as config
from pydantic import SecretStr
from openai import OpenAI

def get_llm(provider="openai", model = None, api_key : str = None, temperature = 0.7):
    if provider == "openai":
        model_name = model or config.DEFAULT_CHAT_MODEL
        return ChatOpenAI(
            openai_api_key = api_key,
            model_name=model_name,
            temperature = temperature
        )
    elif provider == "anthropic":
        model_name = model or "claude-3-sonnet-20240229"
        model_name = fit_anthropic_model(model_name=model_name)
        return ChatAnthropic(
            anthropic_api_key = SecretStr(api_key or ""),
            model = model_name,
            temperature = temperature
        )
    elif provider == "lgai":
        model_name = model or "exaone-3.5"
        return ChatOpenAI(
            openai_api_key=api_key,
            model_name = model_name,
            base_url="https://api.friendli.ai/serverless/v1",
            temperature = temperature
        )
        raise ValueError(f"지원되지 않는 제공자: {provider}")


def get_backend_agent(provider="openai", model=None):
    if provider == "openai":
        model_name = model or config.DEFAULT_CHAT_MODEL
        return ChatOpenAI(
            openai_api_key=config.EMBEDDING_API,
            model_name=model_name,
            temperature=0.7
        )

