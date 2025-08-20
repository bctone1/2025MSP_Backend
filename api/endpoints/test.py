from fastapi import APIRouter, Request
from core.config import GOOGLE_API, CLAUDE_API
from langchain_google_genai import ChatGoogleGenerativeAI
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
