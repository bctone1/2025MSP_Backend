from langchain.prompts import ChatPromptTemplate
from langchain_service.llms.setup import get_llm

def get_session_agent(session_id: str, provider="openai", model=None):
    llm = get_llm(provider, model)

    prompt = ChatPromptTemplate.from_template(
        f"""너는 META LLM MSP 시스템의 AI 에이전트입니다. 세션 ID {session_id}에 대한 작업을 수행합니다.

        너의 목표는 사용자의 질문을 참고하여 해당 대화 세션의 제목을 지어주는 것입니다. 이 제목은 간결하고 정확해야 하며, 질문의 핵심 내용을 나타내야 합니다.

        예시:
        - 질문: '제 코드를 확인하고 오류의 원인을 찾아주세요.'
        - 응답: '오류 원인 분석'

        - 질문: '새로운 웹 프로젝트를 시작하려고 합니다. 기술 스택과 구조를 어떻게 설정할지 고민입니다.'
        - 응답: '웹 프로젝트 기술 스택 설정'

        질문: {{input}}
        """
    )

    # 사용자 입력에 대해 답변을 생성하는 함수
    def agent_executor(input_text: str):
        response = llm(prompt.format(input=input_text))
        return response

    return agent_executor

session_id = "msp_id20250328114640"

# 에이전트 가져오기
agent_executor = get_session_agent(session_id)

# 테스트 입력 (예: 세션 제목을 자동 생성하는 질문)
user_input = "현재 FastAPI 기반 파이썬 프로젝트 진행 중입니다."

# 에이전트 실행 및 결과 출력
response = agent_executor(user_input)

# 결과 출력
print("에이전트 응답:", response)
