from langchain.prompts import ChatPromptTemplate
from langchain_service.llms.setup import get_backend_agent

def generate_title(provider= "openai", model="gpt-3.5-turbo", message = "hello"):
    llm = get_backend_agent(provider, model)

    prompt = ChatPromptTemplate.from_template(
        """
        당신은 META LLM MSP 시스템의 AI 에이전트입니다.
        당신의 목표는 사용자의 질문을 참고하여 해당 대화의 제목(주제)를 지어주는 것입니다.
        이 제목은 간결하고 정확해야 하며, 질문의 핵심 내용을 나타내야 합니다.
        제목은 **공백포함 15자 이내**로 작성해주세요.

        예시 (제목만 출력):
        - 질문: '제 코드를 확인하고 오류의 원인을 찾아주세요.' → 오류 원인 분석
        - 질문: '새로운 웹 프로젝트를 시작하려고 합니다. 기술 스택과 구조를 어떻게 설정할지 고민입니다.' → 웹 프로젝트 기술 스택 설정

        반드시 제목만 출력하세요.  
        "제목 :", "응답 :" 같은 접두어 없이, **제목 텍스트만 단독으로** 출력해야 합니다.

        질문: {input}
        """
    )

    formatted_prompt = prompt.format(input=message)
    raw_response = llm.invoke(formatted_prompt)

    if hasattr(raw_response, "content"):
        content = raw_response.content.strip()
    else:
        content = str(raw_response).strip()

    for prefix in ["제목 :", "제목:", "응답 :", "응답:", "title:", "Title:"]:
        if content.lower().startswith(prefix.lower()):
            content = content[len(prefix):].strip()

    return content
