'''from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import smtplib
from core import get_db_connection
from email.mime.text import MIMEText
from typing import List
import re
from email.mime.multipart import MIMEMultipart
from pinecone import Pinecone, ServerlessSpec
from project.crudProject import create_project
import json
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor


user_router = APIRouter()
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'dudqls327@bctone.kr'  # 발신 이메일 주소
SENDER_PASSWORD = 'mwdc lebe phqy rovf'  # 이메일 비밀번호

@user_router.post('/register')
async def register(request: Request):
    body = await request.json()
    name = body.get('name')
    email = body.get('email')
    password = body.get('password')
    print(name, email, password)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:  # 커서 사용 후 자동으로 닫히도록 with문 사용
            query = """
                INSERT INTO user_table (email, pw, name, role, "group", status, register_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (email, password, name, 'user', 'newUser', 'active'))
            conn.commit()
        conn.close()  # 연결 닫기
        return {"message": "Register Success"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)





@user_router.post('/login')
async def login(request: Request):
    body = await request.json()
    email = body.get('email')
    password = body.get('password')
    print(email, password)
    if not email or not password:
        raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력하세요.")

    try:
        conn = get_db_connection()
        print("db_connected")
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    'SELECT * FROM user_table WHERE email = %s AND pw = %s ORDER BY email ASC',
                    (email, password)
                )
                user_data = cur.fetchone()  # fetchall 대신 fetchone 사용

        if not user_data:
            return JSONResponse(content={'message': '회원정보가 없습니다.'}, status_code=404)

        if user_data["role"] == "admin":
            return JSONResponse(
                content={
                    "message": "관리자님 반갑습니다.",
                    "role": "admin",
                    "email": user_data["email"],
                    "name" : user_data["name"]
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

    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")



@user_router.post("/sendEmail")
async def send_email(request: Request):
    body = await request.json()
    print("Hello")
    email = body.get('email')
    secretCode = body.get('secretCode')
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



@user_router.post('/googlelogin')
async def login(request: Request):
    # 요청 본문 출력
    print("전체 요청 본문:")
    body = await request.json()  # JSON 형식의 본문을 가져오기
    print(body)

    email = body.get('email')
    name = body.get('name')
    image = body.get('image')

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 유저 데이터 조회
                cur.execute('SELECT * FROM user_table WHERE LOWER(email) = LOWER(%s)', (email,))
                user_data = cur.fetchone()
                print(user_data)

                if not user_data:
                    print("유저데이터 삽입 시작")
                    # 커서를 새로 열고 INSERT 작업 실행
                    with conn.cursor() as cur_insert:
                        cur_insert.execute(
                            'INSERT INTO user_table (email, pw, name, role, "group", status, register_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())',
                            (email, 'defaultpassword', name, 'user', 'googleUser','active')
                        )
                        conn.commit()
                    return JSONResponse(
                        content={
                            "message": f"{name}님 반갑습니다! 새 계정이 생성되었습니다.",
                            "role": "user",
                            "email": email,
                        },
                        status_code=200
                    )
                else:
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

    except Exception as e:
        print(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 에러가 발생했습니다.")
'''