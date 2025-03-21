from langchain.chains import ConversationalRetrievalChain
from langchain_service.llms.setup import get_llm
from langchain_service.memory.conversation import get_memory
from langchain_service.vector_stores.setup import get_pgvector_db


def get_qa_chain2(session_id, collection_name="conversation_session", provider="openai", model=None):

    llm = get_llm(provider, model)
    print(f"LLM: {llm}")  # LLM 객체 확인
    vector_db = get_pgvector_db(collection_name)
    print(f"Vector DB: {vector_db}")  # Vector DB 객체 확인
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    print(f"Retriever: {retriever}")  # Retriever 객체 확인
    memory = get_memory(session_id, memory_type="postgres")
    print(f"Memory: {memory}")  # Retriever 객체 확인
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    print(f"QA_CHAIN: {qa_chain}")  # Retriever 객체 확인


def test_qa_chain(session_id, question, collection_name="conversation_logs"):
    # QA 체인 객체 가져오기
    qa_chain = get_qa_chain2(session_id, collection_name)

    if qa_chain is None:
        print("QA chain is None. Check the configuration.")
        return

    # 질의응답 수행
    response = qa_chain.run(question)

    # 답변 및 관련 문서 출력
    print(f"Answer: {response['answer']}")
    print(f"Source Documents: {response['source_documents']}")


# 예시 질문
test_qa_chain(1, "What is the capital of France?")