from langchain.prompts import ChatPromptTemplate
from langchain_service.llm.setup import get_backend_agent
from typing import Callable

def get_file_agent(file: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> Callable[[None], str]:
    llm = get_backend_agent(provider, model)


    prompt = ChatPromptTemplate.from_template(
        """
        당신은 META LLM MSP 시스템의 AI 에이전트입니다.
        아래의 문서 내용을 기반으로 중요한 정보를 요약해주세요:

        문서 내용:
        {content}
        """
    )

    def agent_executor(_: None = None) -> str:
        messages = prompt.format_messages(content=file)
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else response

    return agent_executor