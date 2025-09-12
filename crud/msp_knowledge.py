from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from models import MSP_Knowledge
from typing import List


def create_knowledge(db: Session, origin_name: str, file_path: str, file_type: str, file_size: int, user_id: int,
                     tags: List[str], preview: str):
    new_knowledge = MSP_Knowledge(
        user_id=user_id,
        origin_name=origin_name,
        file_path=file_path,
        type=file_type,
        size=str(file_size),  # DB 컬럼이 String이므로 str로 변환
        tags=tags,
        preview=preview
    )
    db.add(new_knowledge)
    db.commit()
    db.refresh(new_knowledge)  # 새로 생성된 객체를 DB에서 새로 로드
    return new_knowledge


def get_knowledge_by_user(db: Session, user_id: int):
    try:
        knowledges = (
            db.query(MSP_Knowledge)
            .filter(MSP_Knowledge.user_id == user_id)
            .order_by(MSP_Knowledge.created_at.desc())
            .all()
        )

        if not knowledges:
            raise HTTPException(status_code=404, detail="해당 사용자의 Knowledge 데이터가 없습니다.")

        return knowledges
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Knowledge 조회 실패")
