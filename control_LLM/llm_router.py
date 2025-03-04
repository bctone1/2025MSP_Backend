from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from control_LLM.claude_generator import *
import anthropic
import openai
from fastapi import Request
import logging
llm_router = APIRouter()

openai.api_key = "YOUR API KEY"
client = anthropic.Anthropic(
    api_key="YOUR API KEY"
)



class SetProjectRequest(BaseModel):
    messageInput:str

@llm_router.post("/setproject")
def setproject(request:SetProjectRequest):
    description = request.messageInput
    answer = setproject_response(description)
    print(answer)
    return JSONResponse(
        content={
            "projectname": answer["projectname"],
            "description": answer["description"],
            "purpose": answer["purpose"]
        },
        status_code=200
    )


class PromptRequest(BaseModel):
    id:int
    role:str
    content : str

@llm_router.post("/clauderequest")
def generate_prompt(request: PromptRequest):
    print("claude")
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0.0,
            messages=[
                {"role": "user", "content": request.content}
            ])
        print(message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    response_data = {
        "id": 1,
        "role": "assistant",
        "message": message.content[0].text,
        "timestamp": datetime.utcnow().isoformat()
    }
    return JSONResponse(content=response_data)


class RequestConversationRequest(BaseModel):
    messageInput : str

@llm_router.post("/requestconversation")
def requet_conversation(request:RequestConversationRequest):
    mesesageInput = request.messageInput
    answer = set_requirements_response(mesesageInput)
    return JSONResponse(
        content={
            "projectname": answer["title"],
            "description": answer["description"],
            "category": answer["category"],
            "use_cases": answer["use_cases"],
            "constraints": answer["constraints"]
        },
        status_code=200
    )

@llm_router.post("/getconversation")
async def get_conversation(request: Request):
    body = await request.json()
    prompt = body.get("text")
    project = body.get("project")
    get_device()
    conn, cursor = connect_to_DB()
    history = get_history(project, cursor)
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0.0,
            system=f"이전 대화 맥락을 참고해주세요. 이전 대화 기록 : {history}",
            messages=[
                {"role": "user", "content": prompt}
            ])
        print(message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    response = message.content[0].text
    text_embedding(project, cursor, prompt, response)
    return JSONResponse(content=message.content[0].text)
