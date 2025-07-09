from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from core.config import EMBEDDING_API

import os
import openai
import re
os.environ["OPENAI_API_KEY"] = EMBEDDING_API

# 1. 프롬프트 템플릿 정의
template = """
다음은 사용자가 보낸 요청입니다:

"{input}"

이 요청이 어떤 요청인지 번호를 알려주세요.
키워드만 보고 판단하는 것이 아닌, 명확한 맥락을 파악해주세요.
(ex - "이미지 편집하는 프로그램 알려주세요" -> 텍스트 요청 -> 1)
(ex - "HTML에서 비디오 띄우는 법 알려주세요" -> 코드 요청 -> 1 )
(ex - "파이썬에서 이미지 생성하는 방법" -> 코드 요청 -> 1 )
(ex - "이 그림에 대해 설명해주세요." -> 텍스트 요청 -> 1 )

간단한 텍스트, 코드 응답 요청 : 1

이미지 생성 요청 : 2

비디오 생성 요청 : 3

오디오 생성 요청 : 4

복잡한 조사 & 검색 기반 응답 ( 전문적 지식, 최신 정보 필요 ) : 5

복잡한 코드 응답 요청 ( 여러 단계에 거친 코드 작성 ) : 6

분석 에이전트 ( 데이터 분석 및 시각화) : 7

문서 작성 ( 단순한 텍스트 생성을 넘어선 고퀄리티 문서 작성 ) : 8

다른 불필요한 설명 없이 번호만 답변으로 제공해주세요.  
"""

prompt = PromptTemplate(
    input_variables=["input"],
    template=template
)

# 2. LLM 모델 설정
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    streaming=True,
    openai_api_key=EMBEDDING_API
)

# 3. Chain 구성
chain = LLMChain(llm=llm, prompt=prompt)


prompt2 = PromptTemplate(
    input_variables=["input"],
    template="""
다음 문장을 자연스러운 영어로 번역해 주세요.

한국어: {input}
영어:
"""
)

chain2 = LLMChain(llm=llm, prompt=prompt2)

# 4. 함수 정의
def discrimination(input: str) -> int:
    response = chain.run({"input": input}).strip()

    match = re.search(r'\b([1-9][0-9]?)\b', response)

    if match:
        number = int(match.group(1))
        return number
    return 1

def translateToenglish(input:str):
    response = chain2.run({
        "input": input
    })
    return response


def generate_image_with_openai(message: str, model: str) -> str:
    openai.api_key = EMBEDDING_API
    response = openai.images.generate(
        model = model,
        prompt=message,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url