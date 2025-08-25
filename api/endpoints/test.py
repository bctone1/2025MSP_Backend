from fastapi import APIRouter, Request
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from core.config import GOOGLE_API, CLAUDE_API, OPENAI_API
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI
import anthropic

test_router = APIRouter(tags=["test"], prefix="/TEST")

# 랭체인 구글 예시
@test_router.post("/googletest")
async def googletest(request: Request):
    # 요청 정보 출력
    body = await request.json()
    print(body["messageInput"])
    print(body["selected_model"])

    # LLM 호출
    llm = ChatGoogleGenerativeAI(model=body["selected_model"], api_key=GOOGLE_API)
    result = llm.invoke(body["messageInput"])
    print("LLM Result:", result.content)

    return {"response": result.content}

# 엔트로픽 모델 리스트 가져오기
@test_router.post("/getModelList")
async def getModelList(request: Request):
    client = anthropic.Anthropic(api_key=CLAUDE_API)

    result = client.models.list(limit=20)
    print(result)
    return{"response": "엔트로픽 모델리스트 테스트", "models":result}



@test_router.post("/userInputPrompt")
async def userInputPrompt(request: Request):
    body = await request.json()


    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        streaming=False,
        openai_api_key=OPENAI_API
    )

    template = """
    다음은 사용자가 보낸 요청입니다:
    "{input}"

    위 요청을 분석해서 아래 JSON 형식으로만 답변하세요:
    {{
        "language": "...",
        "domain": "...",
        "complexity": "...",
        "accuracyImportance": "...",
        "recommendedModel": "..."
    }}
    """

    prompt = PromptTemplate(
        input_variables=["input"],
        template=template
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.invoke({"input": body["messageInput"]})

    print(response)

    return {"response": response}




