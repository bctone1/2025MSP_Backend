from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import ChatPromptTemplate
from langchain_service.llms.setup import get_llm
from langchain_service.tools.code_tools import execute_python_code, get_database_schema
from typing import List
from langchain.tools import Tool


def get_project_agent(project_id: int, provider="openai", model=None):
    llm = get_llm(provider, model)

    tools = [
        execute_python_code,
        get_database_schema
    ]

    prompt = ChatPromptTemplate.from_template(
        """너는 META LLM MSP 시스템의 AI 에이전트입니다. 프로젝트 ID {project_id}에 대한 작업을 수행합니다.

        너의 목표는 소프트웨어 개발 프로젝트의 분석, 설계, 구현을 지원하는 것입니다.

        다음 도구를 사용할 수 있습니다:
        {tools}

        질문: {input}

        {agent_scratchpad}
        """
    )

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return agent_executor