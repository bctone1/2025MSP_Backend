from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.session import get_db_connection, get_db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from psycopg2.extras import RealDictCursor
import smtplib
import core.config as config
from schemas.user import *
from crud.user import *

user_router = APIRouter()
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

@user_router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    name = request.name
    try:
        user_register(db, email = email, pw = password, name = name)
        return {"message": "Register Success"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@user_router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest, db : Session = Depends(get_db)):
    email = request.email
    password = request.password
    user_data = user_login(db, email, password)
    if not user_data:
        return JSONResponse(content={'message': '회원 정보가 없습니다.'}, status_code=404)
    if user_data["role"] == "admin":
        return JSONResponse(
            content={
                "message": "관리자님 반갑습니다.",
                "role": "admin",
                "email": user_data["email"],
                "name": user_data["name"]
            },
            status_code=200
        )
    elif user_data["role"] == "user":
        return JSONResponse(
            content={
                "message": f"{user_data['name']}님 반갑습니다.",
                "role": "user",
                "email": user_data["email"],
                "name": user_data["name"]
            },
            status_code=200
        )
    else:
        return JSONResponse(content={'message': '역할 정보가 없습니다.'}, status_code=400)


@user_router.post("/sendEmail", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    email = request.email
    secretCode = request.secretCode
    if not secretCode or not email:
        return JSONResponse(content={'message': 'Missing secretCode or email'}, status_code=400)
    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {secretCode}입니다."
    msg = MIMEMultipart()
    msg['From'] = config.SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={'message': '요청되었습니다'}, status_code=200)
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'message': '이메일 전송 실패'}, status_code=500)


@user_router.post('/googlelogin', response_model=GoogleLoginResponse)
async def login(request: GoogleLoginRequest, db : Session = Depends(get_db)):
    email = request.email
    name = request.name

    try:
        user = get_user_data(db, email)

        if not user:
            user = create_google_user(db, email, name)
            return JSONResponse(
                content={
                    "message": f"{user.name}님 반갑습니다! 새 계정이 생성되었습니다.",
                    "role": user.role,
                    "email": user.email,
                },
                status_code=200
            )
        else:
            message = "관리자님 반갑습니다." if user.role == "admin" else f"{user.name}님 반갑습니다."
            return JSONResponse(
                content={
                    "message": message,
                    "role": user.role,
                    "email": user.email,
                    "name": user.name
                },
                status_code=200
            )

    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {e}")
