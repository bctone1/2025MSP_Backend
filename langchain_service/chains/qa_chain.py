from langchain.chains import ConversationalRetrievalChain
from langchain_service.llms.setup import get_llm
from langchain_service.memory.conversation import get_memory
from langchain_service.vector_stores.setup import get_pgvector_db


def get_qa_chain(session_id, collection_name="documents", provider="openai", model=None):
    """
    질의응답 체인을 반환합니다.
    """
    # LLM 모델 가져오기
    llm = get_llm(provider, model)

    # 벡터 스토어 가져오기
    vector_db = get_pgvector_db(collection_name)
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    # 메모리 가져오기
    memory = get_memory(session_id, memory_type="postgres")

    # 체인 생성
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    return qa_chain