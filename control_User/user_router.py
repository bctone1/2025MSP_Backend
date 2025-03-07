from fastapi import APIRouter, Depends, HTTPException, Request
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
import uuid


user_router = APIRouter()

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'dudqls327@bctone.kr'  # 발신 이메일 주소
SENDER_PASSWORD = 'mwdc lebe phqy rovf'  # 이메일 비밀번호



def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        dbname='postgres',
        user='postgres',
        password='1234',
        port='5432',
    )




# class RegisterRequest(BaseModel):
#     name: str
#     password: str
#     email: str
#
# @user_router.post("/register")
# def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
#     try:
#         new_user = register(db = db, user_id = request.name, password=request.password, email=request.email, role="user")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
#     return {"message": "Register Success"}

@user_router.post('/register')
async def login(request: Request):
    body = await request.json()
    name = body.get('name')
    email = body.get('email')
    password = body.get('password')
    print(name,email,password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
                        INSERT INTO "user" (id, pw, email, name)
                        VALUES (%s, %s, %s, %s)
                    """
        cursor.execute(query, (email, password, email, name))
        conn.commit()
        conn.close()
        return {"message": "Register Success"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)








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


# class GoogleLoginRequest(BaseModel):
#     email: str

@user_router.post('/googlelogin')
async def login(request: Request):
    # 요청 본문 출력
    print("전체 요청 본문:")
    body = await request.json()  # JSON 형식의 본문을 가져오기
    print(body)

    email = body['email']
    name = body['name']
    image = body['image']

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT id, email, role FROM "user" WHERE LOWER(email) = LOWER(%s)', (email,))
        user = cur.fetchone()
        print(user)

        if not user:
            print("유저데이터 삽입 시작")
            cur.execute(
                'INSERT INTO "user" (id, email, name, role) VALUES (%s, %s, %s, %s)',
                (email, email, name, 'user')  # 'user'로 기본 역할 설정
            )
            conn.commit()  # 변경사항 저장

            return JSONResponse(
                content={
                    "message": f"{name}님 반갑습니다! 새 계정이 생성되었습니다.",
                    "role": "user",
                    "email": email,
                },
                status_code=200
            )



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
            return JSONResponse(
                content={
                    "message": f"{user_data['id']}님 반갑습니다.",
                    "role": "user",
                    "email": user_data["email"],
                },
                status_code=200
            )
    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
    finally:
        cur.close()
        conn.close()


