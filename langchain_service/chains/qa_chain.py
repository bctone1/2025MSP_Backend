from langchain_service.embeddings.get_vector import text_to_vector
from langchain_service.llms.setup import get_llm
from crud.langchain import *
from langchain.prompts import PromptTemplate

'''
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
'''

def qa_chain(db : Session, session_id, project_id, user_email, conversation, provider="openai", model=None):
    llm = get_llm(provider, model) # LangChain의 get LLM
    vector = text_to_vector(conversation) # LangChain의 get_embedding 기반으로 만든 함수 text_to_vector
    print(f"vector1: {vector}")
    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email, message_role='human', conversation=conversation, vector_memory=vector)
    history_messages = get_chat_history(db, session_id)
    formatted_history = ""
    for msg in history_messages:
        formatted_history += f"{msg['message_role'].capitalize()}: {msg['conversation']}\n"
    prompt = PromptTemplate(input_variables=["history", "input"], template="{history}\nHuman: {input}\nAI:")
    chain = prompt | llm
    response = chain.invoke({"history": formatted_history, "input": conversation})
    print(f"response{response.content}")
    vector2 = text_to_vector(response.content)  # LangChain의 get_embedding 기반으로 만든 함수 text_to_vector
    print(f"vector2: {vector2}")
    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email, message_role='AI', conversation=response.content, vector_memory=vector2)
    return response.content


