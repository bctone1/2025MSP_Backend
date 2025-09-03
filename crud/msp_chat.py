from sqlalchemy.orm import Session

from models import *


def get_sessions_by_user(db: Session, user_id: int):
    return db.query(MSP_Chat_Session).filter(MSP_Chat_Session.user_id == user_id).all()

def get_messages_by_session(db: Session, session_id:int):
    return db.query(MSP_Message).filter(MSP_Message.session_id==session_id).all()

def create_message(db: Session, session_id: int, role: str, content: str, vector_memory=None, extra_data=None):
    new_message = MSP_Message(
        session_id=session_id,
        role=role,
        content=content,
        vector_memory=vector_memory,
        extra_data=extra_data
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)  # 방금 저장한 객체 최신화
    return new_message