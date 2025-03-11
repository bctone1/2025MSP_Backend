from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from control_LLM.claude_generator import *
import anthropic
import openai
from fastapi import Request
import logging
import json


llm_router = APIRouter()

openai.api_key = 'your api key'

client = anthropic.Anthropic(
    api_key="YOUR API KEY"
)


def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        dbname='postgres',
        user='postgres',
        password='1234',
        port='5432',
    )

@llm_router.post('/APIkeyList')
def APIkeyList():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public."api_keys" ORDER BY id ASC')

    # 컬럼명을 가져오기
    column_names = [desc[0] for desc in cur.description]

    # 결과를 딕셔너리 형태로 변환
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return result


@llm_router.post('/providerList')
async def providerList():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
        s.id,
        s.name,
        s.status,
        s.website,
        s.description,
        COALESCE(k.key_count, 0) AS keys_count  -- NULL 방지
    FROM 
        provider_table s
    LEFT JOIN 
        (SELECT provider_id, COUNT(*) AS key_count FROM api_keys GROUP BY provider_id) k
    ON s.name = k.provider_id
    ORDER BY s.id ASC;    
    """)

    # 컬럼명을 가져오기
    column_names = [desc[0] for desc in cur.description]

    # 결과를 딕셔너리 형태로 변환
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return result


@llm_router.post("/setproject")
async def set_project(request: Request):
    data = await request.json()  # 요청 데이터 가져오기
    print(data)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
            다음 프로젝트 설명을 JSON 형식으로 요약해 주세요.
            반드시 아래의 형식을 따르세요.
            {{
                "projectname": "프로젝트명",
                "description": "프로젝트 설명",
                "purpose": "프로젝트 목적"
            }}

            프로젝트 설명: {data}
            """}
        ],
        max_tokens=500
    )

    # GPT 응답을 JSON으로 변환
    parsed_response = json.loads(response['choices'][0]['message']['content'])
    print(parsed_response)

    return JSONResponse(content=parsed_response, status_code=200)


@llm_router.post("/RequestRequirements")
async def RequestRequirements(request: Request):
    data = await request.json()  # 요청 데이터 가져오기
    print(data)
    messageInput = data.get('messageInput')

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
                            다음 프로젝트 요구사항을 참고하여 아래 JSON 형식으로 답변해 주세요.
                            {{
                                "title": "",
                                "description": "",
                                "category": "",
                                "definition": "요구사항 정의 및 방법을 상세하게 작성"
                            }}
                            요구사항: {messageInput}
                            """}
        ],
        max_tokens=500
    )

    # GPT 응답을 JSON으로 변환
    parsed_response = json.loads(response['choices'][0]['message']['content'])
    print(parsed_response)
    return JSONResponse(content=parsed_response, status_code=200)


@llm_router.post("/RequestSystemSettings")
async def RequestSystemSettings(request: Request):
    data = await request.json()  # 요청 데이터 가져오기

    messageInput = data.get('messageInput')
    selectedDescriptions = data.get('selectedDescriptions')
    print("=======================================================")
    print(selectedDescriptions)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
                    다음 프로젝트의 요구사항 및 설명을 참고하여 아래 JSON 형식으로 답변해 주세요.
                    {{
                        "title": "",
                        "description": "",
                        "definition": "요구사항 정의 및 방법을 상세하게 작성"
                    }}
                    요구사항 : {selectedDescriptions},
                    설명: {messageInput}
                    """}
        ],
        max_tokens=500
    )

    # GPT 응답을 JSON으로 변환
    parsed_response = json.loads(response['choices'][0]['message']['content'])
    print(parsed_response)
    return JSONResponse(content=parsed_response, status_code=200)


@llm_router.post("/RequestDBschema")
async def RequestDBschema(request: Request):
    data = await request.json()  # 요청 데이터 가져오기

    messageInput = data.get('messageInput')
    selectedDescriptions = data.get('selectedDescriptions')
    print(selectedDescriptions)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
                        다음 프로젝트의 요구사항 및 설명을 참고하여, DB 테이블 설계를 아래 JSON 형식으로 답변해 주세요.
                        {{
                            "table_name": "",
                            "columns": "
                                "constraints" : "",
                                "data_type" : "",
                                "name" : ""
                            ",
                            "description": "테이블 설명 작성",
                        }}
                        요구사항 : {selectedDescriptions},
                        설명: {messageInput}
                        """}
        ],
        max_tokens=500
    )

    # GPT 응답을 JSON으로 변환
    parsed_response = json.loads(response['choices'][0]['message']['content'])
    print(parsed_response)
    return JSONResponse(content=parsed_response, status_code=200)

@llm_router.post("/Requestapidata")
async def Requestapidata(request: Request):
    data = await request.json()  # 요청 데이터 가져오기

    messageInput = data.get('messageInput')
    selectedDescriptions = data.get('selectedDescriptions')
    selectedSystem = data.get('selectedSystem')
    print(data)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"""
                        다음 프로젝트의 요구사항 및 설명을 참고하여, api 예시 데이터를 아래 JSON 형식으로 답변해 주세요.
                        {{
                            "api_name": "",
                            "apidata": "",
                            "description": "",
                        }}
                        요구사항 : {selectedDescriptions},{selectedSystem}
                        설명: {messageInput}
                        """}
        ],
        max_tokens=500
    )

    # GPT 응답을 JSON으로 변환
    parsed_response = json.loads(response['choices'][0]['message']['content'])
    print(parsed_response)
    return JSONResponse(content=parsed_response, status_code=200)















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
