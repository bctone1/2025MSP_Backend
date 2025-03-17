from langchain_openai import OpenAIEmbeddings
import core.config as config

def get_embeddings():
    """
    기본 임베딩 모델을 반환합니다.
    """
    return OpenAIEmbeddings(
        api_key=config.GPT_API,
        model=config.EMBEDDING_MODEL
    )