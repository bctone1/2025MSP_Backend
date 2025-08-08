from langchain_openai import OpenAIEmbeddings
import core.config as config


def get_embeddings():
    return OpenAIEmbeddings(
        api_key = config.EMBEDDING_API,
        model=config.EMBEDDING_MODEL
    )