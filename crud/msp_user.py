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