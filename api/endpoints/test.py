from fastapi import APIRouter, Request
from core.config import GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI

test_router = APIRouter(tags=["test"], prefix="/TEST")


@test_router.post("/googletest")
async def googletest(request: Request):
    # 요청 정보 출력
    body = await request.json()
    print(body["messageInput"])
    print(body["selected_model"])

    # LLM 호출
    llm = ChatGoogleGenerativeAI(model=body["selected_model"], api_key=GOOGLE_API_KEY)
    result = llm.invoke(body["messageInput"])
    print("LLM Result:", result)

    return {"response": str(result)}


