import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.user import User
from models.llm import ApiKey
from service.sms.send_message import send_message
from fastapi import HTTPException
import bcrypt
import random

SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def user_register(db : Session, email : str, pw : str, name : str, phone_number : str):
    hashed_pw = hash_password(pw)
    new_user = User(
        email = email,
        password=hashed_pw,
        name = name,
        role = 'user',
        group = 'newUser',
        register_at=datetime.utcnow(),
        phone_number = phone_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


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

def get_user_data(db : Session, email : str):
    return db.query(User).filter(User.email.ilike(email)).first()

def generate_random_password():
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f'default_password{random_number}'

def create_google_user(db : Session, email : str, name : str):
    password = generate_random_password()
    hashed_pw = hash_password(password)
    new_user = User(
        email = email,
        password = hashed_pw,
        name = name,
        role = 'socialUser',
        group = 'newUser',
        register_at = datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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


def register_by_admin(db : Session, email : str, name : str, role : str, group : str):
    new_user = User(
        email = email,
        password = "default_password",
        name = name,
        role = role,
        group = group,
        register_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

def delete_user(db : Session, email : str):
    user = db.query(User).filter(User.email == email).first()

    if user:
        db.query(ApiKey).filter(ApiKey.user_id == user.id).delete()
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")

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

def change_profile(db : Session, user_id : int, name : str, group : str, phone_number : str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.group = group,
        user.phone_number = phone_number

    db.commit()
    db.refresh(user)
    return user.password

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

def sms_verfication(db: Session, phone_number : str, phoneCode : str):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user :
        return "이미 가입된 사용자입니다."
    else :
        send_message(phone_number=phone_number, code=phoneCode)
        return "요청이 완료되었습니다."


def findemail_method(db: Session, phone :str, name:str, secretCode:str):
    user = db.query(User).filter(User.phone_number == phone, User.name == name).first()
    if user :
        send_message(phone_number=phone, code = secretCode)
        return user.email
    else:
        return

def delete_apikey(db: Session, key_id : int):
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not api_key:
        raise ValueError("해당 API Key를 찾을 수 없습니다.")

    db.delete(api_key)
    db.commit()

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
