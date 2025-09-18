from dotenv import load_dotenv

from core.config import OPENAI_API
from langchain_service.langsmith import logging
# from langchain_core.messages import HumanMessage
# from langgraph.prebuilt import create_react_agent
from langchain_service.agent import writing_agent, code_agent, research_agent, analysis_agent

from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_service.llm.setup import get_llm

from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import AgentExecutor
from crud.msp_chat import get_messages_by_session  # DB 조회 함수
from schemas.llm import Session

load_dotenv(override=True)
logging.langsmith("react_Agent")

tools = [writing_agent, code_agent, research_agent, analysis_agent ]

def create_agent_executor(tools: list):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "당신은 전문적인 보고서를 작성하는 조력자입니다. "
                "사용자가 제공한 자료와 지시를 바탕으로 논리적이고 체계적인 한국어 보고서를 작성하세요. "
                "보고서는 서론, 본론, 결론 구조를 갖추고, 필요하다면 표나 bullet point를 활용해 가독성을 높이세요.",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)



# DB 기반 세션 히스토리 로드
def get_session_history(session_id: str, db: Session):
    messages = get_messages_by_session(db, session_id)
    if not messages:
        return ChatMessageHistory()

    history = ChatMessageHistory()
    for m in messages:
        if m.role == "user":
            history.add_user_message(m.content)
        elif m.role == "assistant":
            history.add_ai_message(m.content)
        else:
            history.add_message({"role": m.role, "content": m.content})
    return history


def build_agent_with_history(db: Session, agent_executor: AgentExecutor):
    return RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: get_session_history(session_id, db),
        input_messages_key="input",
        history_messages_key="chat_history",
    )


def run_example(db: Session, tools: list):
    # Agent 생성
    agent_executor = create_agent_executor("openai", "gpt-4o", api_key=OPENAI_API, tools=tools)
    agent_with_chat_history = build_agent_with_history(db, agent_executor)

    # 단순 실행 (invoke)
    response = agent_with_chat_history.invoke(
        {"input": "이전의 답변을 SNS 게시글 형태로 100자 내외로 작성하세요."},
        config={"configurable": {"session_id": "abc456"}},
    )

    return response