from langchain.chains import ConversationalRetrievalChain
from langchain_service.llms.setup import get_llm
from langchain_service.memory.conversation import get_memory
from langchain_service.vector_stores.setup import get_pgvector_db


def get_qa_chain(session_id, collection_name="conversation_session", provider="openai", model=None):

    llm = get_llm(provider, model)

    vector_db = get_pgvector_db(collection_name)
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    memory = get_memory(session_id, memory_type="postgres")

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    return qa_chain
