from langchain_community.vectorstores import Chroma, PGVector
from langchain_service.embeddings.setup import get_embeddings
import core.config as config

def get_chroma_db(collection_name="documents"):
    embedding_function = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory=config.CHROMA_PERSIST_DIRECTORY
    )

def get_pgvector_db(collection_name="documents"):
    embedding_function = get_embeddings()
    connection_string = config.VECTOR_DB_CONNECTION
    return PGVector(
        collection_name=collection_name,
        embedding_function=embedding_function,
        connection_string=connection_string
    )