from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from core.config import EMBEDDING_API

import os
import openai
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
(ex - "~한 그림 그려주세요" -> 이미지 생성 요청 -> 2 )

텍스트, 코드 응답 요청 : 1

이미지 생성 요청 : 2

비디오 생성 요청 : 3

오디오 생성 요청 : 4

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
    response = chain.run({
        "input": input
    })
    if "1" in response:
        print("DISCRIMINATION : TEXT")
        return 1
    elif "2" in response:
        print("DISCRIMINATION : IMAGE")
        return 2
    elif "3" in response:
        print("DISCRIMINATION : VIDEO")
        return 3
    elif "4" in response:
        print("DISCRIMINATION : DATA")
        return 4
    elif "5" in response:
        print("DISCRIMINATION : AUDIO")
        return 5
    else :
        return 1

def translateToenglish(input:str):
    response = chain2.run({
        "input": input
    })
    return response


def generate_image_with_openai(message: str, model: str) -> str:
    print(f"[DEBUG] Calling OpenAI API with message: {message}")
    openai.api_key = EMBEDDING_API  # API 키를 전역적으로 설정
    response = openai.images.generate(  # api_key 인수는 제거
        # model="dall-e-2",
        model = model,
        prompt=message,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url