from sqlalchemy.orm import Session, joinedload

from models import MSP_Knowledge


def create_knowledge(db: Session, origin_name: str, file_path: str, file_type: str, file_size: int):
    new_knowledge = MSP_Knowledge(
        origin_name=origin_name,
        file_path=file_path,
        type=file_type,
        size=str(file_size)  # DB 컬럼이 String이므로 str로 변환
    )
    db.add(new_knowledge)
    db.commit()
    db.refresh(new_knowledge)  # 새로 생성된 객체를 DB에서 새로 로드
    return new_knowledge
