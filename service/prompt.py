import json
# from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from core.config import OPENAI_API, DEFAULT_CHAT_MODEL
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model='gpt-4o',temperature=0
    # model_name=DEFAULT_CHAT_MODEL,
    # temperature=0,
    # streaming=False,
    # openai_api_key=OPENAI_API
)


def preview_prompt(input: str, ):
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
        다음은 사용자가 보낸 요청입니다:
        "{input}"
        위 내용을 요약해서 아래 JSON 형식으로만 답변하세요:
        {{
            "title": "...",
            "preview": "..."
        }}
        """
    )
    # chain = LLMChain(llm=llm, prompt=prompt) # LLMChain 클래스는 LangChain 0.1.17부터 사용 중단(deprecated) 되었어요.

    chain = prompt | llm
    response = chain.invoke({"input": input})
    # return response
    # text_output = response["text"] # 구버전 코드
    text_output = response.content
    try:
        parsed = json.loads(text_output)
        return parsed
    except json.JSONDecodeError:
        # JSON이 아닐 경우 fallback 처리
        return {"title": None, "preview": text_output}


def user_input_intent(input: str):
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
        당신은 AI 모델 추천 어드바이저입니다. 
        사용자의 메시지를 분석하여 적절한 LLM 모델을 추천하세요. 

        분석 기준:
        - 언어 (한국어 / 영어 / 혼합)
        - 도메인 (일상, 금융, 법률, 의료, 학술 등)
        - 복잡도 (낮음 / 중간 / 높음)
        - 정확도 중요도 (낮음 / 중간 / 높음)
        - 창의성 필요성 (낮음 / 중간 / 높음)
        - 긴급성 (즉시 응답 / 고품질 우선)

        입력 메시지:
        "{input}"

        출력은 반드시 아래 JSON 형식으로만 답변하세요:
        {{
            "analysis": {{
                "language": "...",
                "domain": "...",
                "complexity": "...",
                "accuracy_importance": "...",
                "creativity_need": "...",
                "urgency": "..."
            }},
            "recommended_model": "..."
        }}
        """
    )
    chain = prompt | llm
    response = chain.invoke({"input": input})
    text_output = response.content   # ✅ 모델의 답변 텍스트
    print(text_output)

    try:
        parsed = json.loads(text_output)
        return parsed
    except json.JSONDecodeError:
        # JSON이 아닐 경우 fallback 처리
        return {"analysis": None, "recommended_model": DEFAULT_CHAT_MODEL}