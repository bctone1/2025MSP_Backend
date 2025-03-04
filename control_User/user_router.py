from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from database import get_db
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date
from .crud_user import register, authenticate_user
from control_LLM.claude_generator import setproject_response
import anthropic
import openai
import psycopg2
import smtplib
from email.mime.text import MIMEText
from typing import List
import re
from email.mime.multipart import MIMEMultipart
from pinecone import Pinecone, ServerlessSpec
from project.crudProject import create_project
import json

user_router = APIRouter()

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = "YOUR EMAIL"
SENDER_PASSWORD = "YOUR KEY"


class RegisterRequest(BaseModel):
    name: str
    password: str
    email: str

@user_router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        new_user = register(db = db, user_id = request.name, password=request.password, email=request.email, role="user")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    return {"message": "Register Success"}










class LoginRequest(BaseModel):
    email: str
    password: str

@user_router.post('/login')
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)

    if user is None:
        print("user is None")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.role == "admin":
        return JSONResponse(content={"message": "관리자님 반갑습니다.", "role": "admin", "name": f"{user.id}", "email": f"{user.email}"}, status_code=200)
    elif user.role == "user":
        return JSONResponse(content={"message": f"{user.id} 반갑습니다.", "role": "user", "name": f"{user.id}", "email": f"{user.email}"}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="회원정보가 없습니다.")


class EmailRequest(BaseModel):
    email: str
    secretCode:str

@user_router.post("/sendEmail")
def send_email(request: EmailRequest, db: Session = Depends(get_db)):
    print("Hello")
    email = request.email
    secretCode = request.secretCode
    if not secretCode or not email:
        return JSONResponse(content={'message': 'Missing secretCode or email'}, status_code=400)
    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {secretCode}입니다."
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={'message': '요청되었습니다'}, status_code=200)
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'message': '이메일 전송 실패'}, status_code=500)


class GoogleLoginRequest(BaseModel):
    email: str

@user_router.post('/googlelogin')
def login(request: GoogleLoginRequest):
    email = request.email
    print(f"로그인 요청 이메일: {email}")

    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='msp_database',
            user='postgres',
            password='3636',
            port='5433',
        )
        cur = conn.cursor()

        cur.execute('SELECT id, email, role FROM "user" WHERE LOWER(email) = LOWER(%s)', (email,))
        user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="회원정보가 없습니다.")

        user_data = {
            "id": user[0],
            "email": user[1],
            "role": user[2],
        }

        if user_data["role"] == "admin":
            return JSONResponse(
                content={
                    "message": "관리자님 반갑습니다.",
                    "role": "admin",
                    "email": user_data["email"],
                },
                status_code=200
            )
        elif user_data["role"] == "user":
            return JSONResponse(
                content={
                    "message": f"{user_data['id']}님 반갑습니다.",
                    "role": "user",
                    "email": user_data["email"],
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=403, detail="권한이 정의되지 않았습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
    finally:
        cur.close()
        conn.close()


