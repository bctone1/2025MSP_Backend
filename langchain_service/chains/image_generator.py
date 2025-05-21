from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from core.config import EMBEDDING_API
# OpenAI API 키 설정
import os
import openai
os.environ["OPENAI_API_KEY"] = EMBEDDING_API

# 1. 프롬프트 템플릿 정의
template = """
다음은 사용자가 보낸 요청입니다:

"{input}"

이 요청이 이미지 생성을 위한 요청인지 판단해주세요.

이미지 생성 요청이면 "1", 아니면 "2"만 대답해주세요.
다른 설명은 하지 말고 숫자만 출력하세요.
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
        return 1
    elif "2" in response:
        return 2
    else :
        return 2

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