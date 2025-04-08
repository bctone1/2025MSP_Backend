import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.project import User
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

def user_register(db : Session, email : str, pw : str, name : str):
    hashed_pw = hash_password(pw)
    new_user = User(
        email = email,
        password=hashed_pw,
        name = name,
        role = 'user',
        group = 'newUser',
        register_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def user_login(db: Session, email: str, pw: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    # 비밀번호 암호화 여부 판단
    if user.password.startswith("$2b$"):  # bcrypt 해시 형식이면
        if verify_password(pw, user.password):
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
    else:
        # 암호화 안 된 경우 (기존 방식) 평문 비교
        if user.password == pw:
            # 로그인 성공 후 비밀번호 해시로 업데이트 (마이그레이션)
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
        role = 'googleUser',
        group = 'newUser',
        register_at = datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_member(db : Session):
    members = db.execute(select(User.id, User.email, User.password, User.name, User.role, User.group, User.register_at)).all()

    return {
        "members": [
            {
                "id" : m.id,
                "name": m.name,
                "email": m.email,
                "role": m.role,
                "group": m.group
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
    return new_user

def delete_user(db : Session, email : str):
    user = db.query(User).filter(User.email == email).first()

    if user:
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")

def change_user_info(db: Session, name : str, email : str, role : str, group : str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.name = name,
        user.role = role,
        user.group = group

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
        "group" : user.group
    }

def change_password(db : Session, id : int, current_pw : str, new_pw : str):
    user = db.query(User).filter(User.id == id).first()
    if user.password == current_pw:
        user.password = new_pw
        db.commit()
        db.refresh(user)
    return user.password

def change_profile(db : Session, id : int, name : str, group : str):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.group = group
    db.commit()
    db.refresh(user)
    return user.password