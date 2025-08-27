from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from core.config import GOOGLE_API, CLAUDE_API, OPENAI_API
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI
from fastapi.responses import JSONResponse
import anthropic


from database.session import get_db #DB 커넥션




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


# 사용자 의도파악 프롬프트 예시
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
    # print(response)
    return {"response": response}


# Rag 파일업로드 요청
@test_router.post("/uploadRAG")
async def uploadRAG(request: Request, file: UploadFile = File(...)):
    form_data = await request.form()
    project_id = form_data.get("project_id")
    # project_id = int(project_id) if project_id is not None else None
    user_email = form_data.get("user_email")
    session_id = form_data.get("session_id")
    print(form_data)

    print(file.filename)
    # agent = get_file_agent(origin_name)
    return {"filename": file.filename}


# 로그인
@test_router.post("/MSPLogin")
async def MSPLogin(request: Request):
    body = await request.json()
    # print(body["user_email"])
    # print(body["user_pw"])
    # print(body["user_name"])
    print(body)
    if body["loginMethod"] =="user" and body["user_email"] == "user" and body["user_pw"] == "123":
        return {
            "response": "유저 로그인 성공",
            "status": True,
            "name": body["user_name"],
            "email": body["user_email"],
            "role" : body["loginMethod"]
        }
    elif body["loginMethod"] =="admin" and body["user_email"] =="admin" and body["user_pw"] == "123":
        return {
            "response": "관리자 로그인 성공",
            "status": True,
            "name": body["user_name"],
            "email": body["user_email"],
            "role": body["loginMethod"]
        }
    return JSONResponse(content={'message': '회원 정보가 없습니다.'}, status_code=404)


# 소셜로그인
@test_router.post("/MSPSocialLogin")
async def MSPSocialLogin(request: Request):
    body = await request.json()
    print(body)

    return {"response":"소셜 로그인 성공"}


# 아래 메서드에서 사용되는 모듈
from crud.user import *
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart

# SMTP 환경변수 (이메일 전송용)
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

# 이메일 인증 요청
@test_router.post("/MSPSendEmail")
async def MSPSendEmail(request: Request):
    body = await request.json()
    print(body)
    email = body.get("email")
    secretCode = body.get("secretCode")

    return JSONResponse(content={"response": "이메일 확인 후 인증번호를 입력해주세요", "result": True}, status_code=200)

    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {body["secretCode"]}입니다."
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = config.SENDER_EMAIL, email, subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={"response": "중복확인 되었습니다! 인증번호를 입력해주세요.", "result":True}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'response': f'이메일 전송 실패 : {str(e)}', "result":False}, status_code=500)

# 이메일 중복체크 요청
@test_router.post("/MSPCheckEmail")
async def MSPCheckEmail(request: Request):
    body = await request.json()
    print(body)
    email = body.get("email")

    if email == "dudqls327@naver.com":
        return {
            "response": "이미 가입된 이메일 입니다!",
            "result": False
        }
    else :
        return {
            "response": "사용 가능한 이메일 입니다!",
            "result": True
        }

# 회원가입 요청
@test_router.post("/MSPRegister")
async def MSPRegister(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print(body)

    return {
        "response": "가입이 완료되었습니다!",
        "result": True
    }