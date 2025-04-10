from langchain_service.embeddings.get_vector import text_to_vector
from langchain_service.llms.setup import get_llm
from langchain_service.memory.relevant_message import get_relevant_messages
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.output_parsers import StrOutputParser
from crud.langchain import *
from langchain.prompts import PromptTemplate
from langchain_service.llms.get_cost import *
from crud.user import update_usage
'''
def qa_chain(db : Session, session_id, project_id, user_email, conversation, provider="openai", model=None):
    llm = get_llm(provider, model) # LangChain의 get LLM
    vector = text_to_vector(conversation) # LangChain의 get_embedding 기반으로 만든 함수 text_to_vector
    print(f"vector1: {vector}")
    
    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email, message_role='user', conversation=conversation, vector_memory=vector)
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
    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email, message_role='assistant', conversation=response.content, vector_memory=vector2)
    return response.content



'''
'''
def qa_chain(db: Session, session_id, project_id, user_email, conversation, provider="openai", model=None):
    llm = get_llm(provider, model)
    vector = text_to_vector(conversation)

    relevant_messages = get_relevant_messages(db, session_id, vector, top_n=5)

    formatted_history = "\n".join(
        [f"{msg['message_role'].capitalize()}: {msg['conversation']}" for msg in relevant_messages]
    )

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="{history}\nHuman: {input}\nAI:"
    )

    chain = prompt | llm | StrOutputParser()

    with get_openai_callback() as cb:
        response_text = chain.invoke({"history": formatted_history, "input": conversation})

        print(f"[LLM 사용량] prompt: {cb.prompt_tokens} / completion: {cb.completion_tokens} / total: {cb.total_tokens} / cost: ${cb.total_cost:.6f}")


    vector2 = text_to_vector(response_text)

    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                message_role='user', conversation=conversation, vector_memory=vector)

    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                message_role='assistant', conversation=response_text, vector_memory=vector2)

    return response_text


'''


def qa_chain(db: Session, session_id, project_id, user_email, conversation, provider="openai", model=None):
    llm = get_llm(provider, model)
    vector = text_to_vector(conversation)
    relevant_messages = get_relevant_messages(db, session_id, vector, top_n=5)

    formatted_history = "\n".join(
        [f"{msg['message_role'].capitalize()}: {msg['conversation']}" for msg in relevant_messages]
    )

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="{history}\nHuman: {input}\nAI:"
    )
    chain = prompt | llm | StrOutputParser()

    # 비용 계산 분기 처리
    if provider == "openai":
        with get_openai_callback() as cb:
            response_text = chain.invoke({"history": formatted_history, "input": conversation})
            update_usage(db = db, user_email = user_email, provider = provider, usage = cb.total_tokens)
            print(f"[LLM 사용량 - OpenAI] prompt: {cb.prompt_tokens} / completion: {cb.completion_tokens} / total: {cb.total_tokens} / cost: ${cb.total_cost:.6f}")
    elif provider == "anthropic":
        prompt_tokens = count_tokens(formatted_history)
        response_text = chain.invoke({"history": formatted_history, "input": conversation})
        completion_tokens = count_tokens(response_text)
        cost_data = estimate_claude_cost(model, prompt_tokens, completion_tokens)
        update_usage(db=db, user_email=user_email, provider=provider, usage=cost_data['total'])
        print(f"[LLM 사용량 - Claude] prompt: {cost_data['prompt']} / completion: {cost_data['completion']} / total: {cost_data['total']} / cost: ${cost_data['cost']:.6f}")
    else:
        # 기타 모델 대응 가능
        response_text = chain.invoke({"history": formatted_history, "input": conversation})
        print("[LLM 사용량] 추적 불가: 미지원 provider")

    # 저장
    vector2 = text_to_vector(response_text)
    print(f"✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ LENGTH OF VEC : {vector}✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅")
    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                message_role='user', conversation=conversation, vector_memory=vector)

    add_message(db=db, session_id=session_id, project_id=project_id, user_email=user_email,
                message_role='assistant', conversation=response_text, vector_memory=vector2)

    return response_text








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