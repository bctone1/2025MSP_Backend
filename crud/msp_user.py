from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from models import MSP_USER   # 모델이 정의된 모듈에서 import

import bcrypt
import random
from datetime import datetime, UTC
from sqlalchemy import select, func
from models.user import User
from models.llm import ApiKey
from service.sms.send_message import send_message
from fastapi import HTTPException
import core.config as config

# CREATE
def create_user(
        db: Session, email: str, password_hash: str, name: Optional[str] = None,role: Optional[str] = "user", terms_agreed: bool = False,marketing_agreed: bool = False) -> MSP_USER:
    new_user = MSP_USER(
        email=email,
        password_hash=password_hash,
        name=name,
        role=role,
        terms_agreed=terms_agreed,
        marketing_agreed=marketing_agreed
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise ValueError("이미 존재하는 이메일입니다.")

# READ - 단일 조회
def get_user_by_id(db: Session, user_id: int) -> Optional[MSP_USER]:
    return db.query(MSP_USER).filter(MSP_USER.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[MSP_USER]:
    return db.query(MSP_USER).filter(MSP_USER.email == email).first()

# READ - 전체 조회
def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[MSP_USER]:
    return db.query(MSP_USER).offset(skip).limit(limit).all()

# UPDATE
def update_user(db: Session, user_id: int, **kwargs) -> Optional[MSP_USER]:
    user = db.query(MSP_USER).filter(MSP_USER.user_id == user_id).first()
    if not user:
        return None
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

# DELETE
def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(MSP_USER).filter(MSP_USER.user_id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

# Create social user
def create_social_user(
    db: Session,
    email: str,
    name: str,
    profile_image: str = None,
    role: str = "user"
) -> MSP_USER:
    """
    소셜 로그인용 유저 생성 또는 기존 유저 조회
    """
    # 1. 기존 유저 확인
    user = db.query(MSP_USER).filter(MSP_USER.email == email).first()
    if user:
        return user  # 이미 존재하면 그대로 반환 (로그인 처리)

    # 2. 신규 유저 생성
    new_user = MSP_USER(
        email=email,
        password_hash="blogcodi0318",
        name=name,
        role=role
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise ValueError("유저 생성 중 오류 발생")

######################################
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD


# 입력 비밀번호를 bcrypt 해시로 변환
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 평문 비밀번호와 해시된 비밀번호 일치 여부 확인
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 일반 사용자 회원가입 (비밀번호 해시 저장)
def user_register(db : Session, email : str, pw : str, name : str, phone_number : str):
    hashed_pw = hash_password(pw)
    new_user = User(
        email = email,
        password=hashed_pw,
        name = name,
        role = 'user',
        group = 'newUser',
        register_at=datetime.now(UTC),
        phone_number = phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

# 사용자 로그인 (bcrypt 검증 또는 평문 비번 승격)
def user_login(db: Session, email: str, pw: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if user.password.startswith("$2b$"):
        if verify_password(pw, user.password):
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
    else:
        if user.password == pw:
            user.password = hash_password(pw)
            db.commit()
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }

    return None

# 이메일로 사용자 데이터 조회
def get_user_data(db : Session, email : str):
    return db.query(User).filter(User.email.ilike(email)).first()

# 기본 랜덤 비밀번호 생성
def generate_random_password():
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f'default_password{random_number}'

# 구글 로그인 계정 생성 (랜덤 비번 자동 발급)
def create_google_user(db : Session, email : str, name : str):
    password = generate_random_password()
    hashed_pw = hash_password(password)
    new_user = User(
        email = email,
        password = hashed_pw,
        name = name,
        role = 'socialUser',
        group = 'newUser',
        register_at = datetime.now(UTC)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 전체 사용자 목록 조회
def get_member(db : Session):
    members = db.execute(select(User.id, User.email, User.password, User.name, User.role, User.group, User.register_at, User.phone_number)).all()

    return {
        "members": [
            {
                "id" : m.id,
                "name": m.name,
                "email": m.email,
                "role": m.role,
                "group": m.group,
                "phone_number" : m.phone_number
            } for m in members
        ]
    }

# 관리자가 신규 사용자 등록 (비번은 default_password)
def register_by_admin(db : Session, email : str, name : str, role : str, group : str):
    new_user = User(
        email = email,
        password = "default_password",
        name = name,
        role = role,
        group = group,
        register_at=datetime.now(UTC)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

# 사용자 삭제 (관련 API Key도 삭제)
def delete_user(db : Session, email : str):
    user = db.query(User).filter(User.email == email).first()

    if user:
        db.query(ApiKey).filter(ApiKey.user_id == user.id).delete()
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")

# 사용자 정보 변경 (이름/권한/그룹/전화번호)
def change_user_info(db: Session, name : str, email : str, role : str, group : str, phone_number:str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.name = name,
        user.role = role,
        user.group = group,
        user.phone_number = phone_number

        db.commit()
        db.refresh(user)
        return user
    else:
        return None

# 특정 사용자 상세 정보 조회
def get_user_info(db: Session, email : str):
    user = db.query(User).filter(User.email == email).first()
    return {
        "id": user.id,
        "email": user.email,
        "password" : user.password,
        "name" : user.name,
        "role" : user.role,
        "group" : user.group,
        "phone_number": user.phone_number
    }

# 비밀번호 변경 (현재 비번 확인 후 갱신)
def change_password(db : Session, user_id : int, current_pw : str, new_pw : str):
    user = db.query(User).filter(User.id == user_id).first()
    hashed_pw = hash_password(new_pw)
    if user.password.startswith("$2b$"):
        if verify_password(current_pw, user.password):
            user.password = hashed_pw
            db.commit()
            db.refresh(user)
            return "비밀번호가 변경되었습니다!"
        else :
            return "현재 비밀번호가 잘못되었습니다."
    else :
        return "관리자 권한으로 생성된 계정입니다."

# 비밀번호 재설정 (이메일 기반)
def find_password(db : Session, email : str, new_pw : str):
    user = db.query(User).filter(User.email == email).first()
    hashed_pw = hash_password(new_pw)
    if user.password.startswith("$2b$"):
        user.password = hashed_pw
        db.commit()
        db.refresh(user)
        return "비밀번호가 변경되었습니다!"
    else :
        return "관리자 권한으로 생성된 계정입니다."

# 프로필 변경 (이름/그룹/전화번호)
def change_profile(db : Session, user_id : int, name : str, group : str, phone_number : str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.group = group,
        user.phone_number = phone_number

    db.commit()
    db.refresh(user)
    return user.password

# API Key 사용량 업데이트
def update_usage(db : Session, user_email : str, provider : str, usage : int):
    user = db.query(User).filter(User.email == user_email).first()
    id = user.id
    api = db.query(ApiKey).filter(
        ApiKey.user_id == id,
        ApiKey.status == 'Active',
        func.lower(ApiKey.provider_name) == provider.lower()
    ).first()
    total_usage = api.usage_count + usage
    if api.usage_limit > total_usage :
        api.usage_count = total_usage
        db.commit()
        db.refresh(user)
    return total_usage

# 새 API키 등록
def add_apikey(db: Session, api_key : str, provider_id : int, provider_name : str, usage_limit : int, usage_count:int, user_id:int):
    new_apikey = ApiKey(
        api_key = api_key,
        provider_id = provider_id,
        provider_name = provider_name,
        usage_limit = usage_limit,
        usage_count = usage_count,
        user_id = user_id,
        status = "Active"
    )
    db.add(new_apikey)
    db.commit()
    db.refresh(new_apikey)
    return "success"

# 휴대폰 번호 인증 요청
def sms_verfication(db: Session, phone_number : str, phoneCode : str):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user :
        return "이미 가입된 사용자입니다."
    else :
        send_message(phone_number=phone_number, code=phoneCode)
        return "요청이 완료되었습니다."

# 전화번호 + 이름 으로 이메일 찾기
def findemail_method(db: Session, phone :str, name:str, secretCode:str):
    user = db.query(User).filter(User.phone_number == phone, User.name == name).first()
    if user :
        send_message(phone_number=phone, code = secretCode)
        return user.email
    else:
        return

# 특정 API 찾기
def delete_apikey(db: Session, key_id : int):
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not api_key:
        raise ValueError("해당 API Key를 찾을 수 없습니다.")

    db.delete(api_key)
    db.commit()

# 신규 사용자 기본 API 생성(앤트로픽)
def change_apikey(db: Session, key_id : int, api_key : str):
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if key:
        key.api_key = api_key
    db.commit()
    db.refresh(key)

def add_default_apikey(db : Session, user_id : int):
    new_apikey = ApiKey(
        api_key='Default API Key',
        provider_id=2,
        provider_name = 'Anthropic',
        usage_limit = 500,
        usage_count = 0,
        user_id = user_id,
        status = "Active"
    )
    db.add(new_apikey)
    db.commit()
    db.refresh(new_apikey)
    return "success"


















