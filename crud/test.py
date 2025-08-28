from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from models import MSP_USER   # 모델이 정의된 모듈에서 import

# CREATE
def create_user(db: Session, email: str, password_hash: str, name: Optional[str] = None,role: Optional[str] = "user", terms_agreed: bool = False,marketing_agreed: bool = False) -> MSP_USER:
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
