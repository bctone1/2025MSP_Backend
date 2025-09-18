import json

from langchain_service.langsmith import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from core.config import OPENAI_API, DEFAULT_CHAT_MODEL
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
# import re
# from fastapi.responses import JSONResponse

logging.langsmith("Garam_RAG")

llm = ChatOpenAI(
    model='gpt-4o', temperature=0,
    # model_name=DEFAULT_CHAT_MODEL,
    # streaming=False,
    openai_api_key=OPENAI_API
)


def get_answer_with_knowledge(
    llm, user_input: str, knowledge_rows: list[dict], max_chunks: int = 4
) -> str:
    if not knowledge_rows:
        return "관련된 지식이 없어 답변할 수 없습니다."

    # 1. similarity 낮은 순으로 정렬 후 상위 max_chunks 선택
    top_chunks = sorted(knowledge_rows, key=lambda x: x["similarity"])[:max_chunks]
    knowledge_texts = "\n\n".join([x["chunk_text"] for x in top_chunks])
    print("가공된 데이터:", knowledge_texts)

    # ChatPromptTemplate 사용
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """당신은 가람포스텍 RAG 시스템의 응답자입니다.
            아래는 검색된 지식베이스 내용입니다:
            
            {knowledge_texts}

            규칙:
            1. 제공된 지식만 사용하여 답변할 것. 질문 문장을 그대로 반복하지 말 것.
            2. 원문의 핵심 구절(사훈, 표어, 원칙 등)은 반드시 그대로 포함.
            3. 요약은 허용하되 핵심 구절은 삭제·변형하지 말 것.
            4. 답변은 번호 목록 또는 불릿포인트로 구조화해 깔끔하게 출력.
            5. '원문 인용' 같은 라벨은 출력하지 말 것.
            6. 최대 10줄 이내로 유지.""",
        ),
        ("human", "{user_input}"),
    ])

    chain = prompt | llm
    response = chain.invoke({
        "user_input": user_input,
        "knowledge_texts": knowledge_texts
    })

    text_output = response.content
    print("데이터와 함께 요청 결과:", text_output)
    # return JSONResponse(content={"answer": text_output})
    return text_output



def pdf_preview_prompt(file_path: str) -> dict:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    # 앞 페이지 텍스트를 합치기
    full_text = "\n".join([doc.page_content for doc in documents])
    short_text = full_text[:3000]  # 앞 3000자 정도만 LLM에 전달

    prompt = PromptTemplate(
        input_variables=["input_text"],
        template="""
                  "{input_text}"
                  위 내용을 요약해서 아래 JSON 형식으로만 답변하세요:
                  {{
                      "tags": ["...","...","...","..."],
                      "preview": "...",
                  }}
                  """
    )

    chain = prompt | llm
    response = chain.invoke({"input_text": short_text})
    text_output = response.content
    try:
        text_output = text_output.replace("```json", "").replace("```", "").strip()
        text_output = json.loads(text_output)
        return text_output
    except json.JSONDecodeError:
        # JSON이 아닐 경우 fallback 처리
        return {"tags": "", "preview": "text_output"}


def preview_prompt(input: str):
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
        text_output = text_output.replace("```json", "").replace("```", "").strip()
        text_output = json.loads(text_output)
        return text_output
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
    text_output = response.content  # ✅ 모델의 답변 텍스트
    print(text_output)

    try:
        text_output = text_output.replace("```json", "").replace("```", "").strip()
        text_output = json.loads(text_output)
        return text_output
    except json.JSONDecodeError:
        # JSON이 아닐 경우 fallback 처리
        return {"analysis": None, "recommended_model": DEFAULT_CHAT_MODEL}
