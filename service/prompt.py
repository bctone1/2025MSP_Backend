import json

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from core.config import OPENAI_API, DEFAULT_CHAT_MODEL
from langchain_openai import ChatOpenAI
import re

llm = ChatOpenAI(
    model='gpt-4o', temperature=0,
    # model_name=DEFAULT_CHAT_MODEL,
    # temperature=0,
    # streaming=False,
    openai_api_key=OPENAI_API
)


def get_answer_with_knowledge(llm, user_input: str, knowledge_rows: list[dict], max_chunks: int = 3) -> str:
    if not knowledge_rows:
        return user_input

    # 1. similarity가 낮은 순서대로 정렬 (낮을수록 더 관련 있음)
    top_chunks = sorted(knowledge_rows, key=lambda x: x["similarity"])[:max_chunks]
    # knowledge_texts = "\n\n".join([f"data {i + 1}:\n{x['chunk_text']}" for i, x in enumerate(top_chunks)])
    knowledge_texts = "\n\n".join([x['chunk_text'] for x in top_chunks])
    print("가공된 데이터 : ", knowledge_texts)
    prompt = PromptTemplate(
        input_variables=["user_input", "knowledge_texts"],
        template="""
        당신은 업로드된 문서(PDF)에서 추출된 지식 기반을 활용하여 사용자의 질문에 답변하는 전문가 비서입니다.  
    
        [사용자 질문]  
        {user_input}  
    
        [참고 자료]  
        아래 텍스트는 사용자가 업로드한 PDF에서 벡터 검색을 통해 질문과 가장 유사도가 높은 부분을 선별한 것입니다.  
        {knowledge_texts}  
    
        [답변 지침]  
        1. 반드시 참고 자료를 최우선으로 활용하세요.  
        2. 자료에 없는 내용은 추측하지 말고, "제공된 자료에서는 해당 정보를 찾을 수 없습니다."라고 명시하세요.  
        3. 불필요한 반복이나 장황한 설명은 피하고, 사용자가 이해하기 쉽게 간결하고 구체적으로 답변하세요.  
        4. 전문 용어는 풀어서 설명하되, 원문 표현도 함께 제시하세요.  
        5. 답변은 한국어로 작성하세요.  
    
        [최종 답변]  
        """
    )
    chain = prompt | llm
    response = chain.invoke({"user_input": user_input, "knowledge_texts": knowledge_texts})
    text_output = response.content
    print("데이터와 함께 요청 결과1 : ", text_output)
    return text_output


def pdf_preview_prompt(file_path: str) -> dict:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    # 앞 페이지 텍스트를 합치기
    full_text = "\n".join([doc.page_content for doc in documents])
    short_text = full_text[:6000]  # 앞 3000자 정도만 LLM에 전달

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
    당신은 JSON 포맷 요약기를 수행하는 도우미입니다.  
    아래는 사용자가 보낸 요청입니다:
    "{input}"

    작업 지시사항:
    1. 입력 내용을 읽고 핵심 주제를 간결하게 "title"에 담으세요 (짧고 직관적, 10자 이내 권장).
    2. 입력 내용을 요약하여 "preview"에 담으세요 (2~3문장, 핵심만 포함).
    3. 반드시 JSON 형식만 출력하세요. 그 외 설명, 텍스트, 코드블록 표시는 금지합니다.

    출력 예시:
    {{
        "title": "파일 선택 요약",
        "preview": "사용자가 새로운 대화를 시작하면서 선택한 파일을 참조하려고 합니다."
    }}

    이제 아래 입력을 JSON으로 요약하세요:
    "{input}"
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
