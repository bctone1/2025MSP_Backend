from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
import anthropic
from core.config import CLAUDE_API, OPENAI_API, EMBEDDING_API
from fastapi.responses import JSONResponse
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
import core.config as config
from langchain.chains import RetrievalQA
from service.prompt import preview_prompt


# SMTP 환경변수 (이메일 전송용)
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

service_router = APIRouter(tags=["msp_service"], prefix="/MSP_SERVICE")



# 엔트로픽 모델 리스트 가져오기
@service_router.post("/getModelList")
async def getModelList(request: Request):
    client = anthropic.Anthropic(api_key=CLAUDE_API)

    result = client.models.list(limit=20)
    print(result)
    return {"response": "엔트로픽 모델리스트 테스트", "models": result}

# 이메일 인증 요청
@service_router.post("/MSPSendEmail")
async def MSPSendEmail(request: Request):
    body = await request.json()
    print(body)
    email = body.get("email")
    secretCode = body.get("secretCode")

    # return JSONResponse(content={"response": "이메일 확인 후 인증번호를 입력해주세요", "result": True}, status_code=200)

    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {secretCode}입니다."
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = config.SENDER_EMAIL, email, subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={"response": "중복확인 되었습니다! 인증번호를 입력해주세요.", "result": True}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'response': f'이메일 전송 실패 : {str(e)}', "result": False}, status_code=500)
