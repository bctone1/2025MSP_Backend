from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from models import MSP_Knowledge, MSP_KnowledgeChunk
from typing import List, Sequence
from models import MSP_Knowledge, MSP_Chat_Session
from typing import List

from models.associations import session_knowledge_association

def get_session_knowledge_association(db: Session, session_id: int):
    session_obj = db.query(MSP_Chat_Session).filter(MSP_Chat_Session.id == session_id).first()
    if not session_obj:
        return []
    return [k.id for k in session_obj.knowledges]


def add_session_knowledge_association(db: Session, session_id: int, knowledge_ids: list[int]):
    new_associations = []

    # dict로 들어올 경우 id만 추출
    cleaned_ids = []
    for kid in knowledge_ids:
        if isinstance(kid, dict):
            cleaned_ids.append(kid.get("id"))  # {"id": 23} → 23
        else:
            cleaned_ids.append(kid)

    for kid in cleaned_ids:
        # 이미 존재하는지 확인
        exists_stmt = db.query(session_knowledge_association).filter_by(
            session_id=session_id,
            knowledge_id=kid
        ).first()

        if exists_stmt:
            # 이미 존재하면 건너뜀
            continue

        # 존재하지 않으면 삽입
        stmt = session_knowledge_association.insert().values(
            session_id=session_id,
            knowledge_id=kid
        )
        db.execute(stmt)
        new_associations.append(kid)

    db.commit()
    return new_associations


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
    from sqlalchemy import func
    knowledges_with_count = (
        db.query(
            MSP_Knowledge,
            func.count(MSP_KnowledgeChunk.id).label("chunk_count")
        )
        .outerjoin(MSP_KnowledgeChunk, MSP_Knowledge.id == MSP_KnowledgeChunk.knowledge_id)
        .filter(MSP_Knowledge.user_id == user_id)
        .group_by(MSP_Knowledge.id)
        .order_by(MSP_Knowledge.created_at.desc())
        .all()
    )

    if not knowledges_with_count:
        raise HTTPException(status_code=404, detail="해당 사용자의 Knowledge 데이터가 없습니다.")

    result = []
    for k, chunk_count in knowledges_with_count:
        result.append({
            "id": k.id,
            "origin_name": k.origin_name,
            "file_path": k.file_path,
            "type": k.type,
            "size": k.size,
            "tags": k.tags,  # 여기 추가
            "preview":k.preview,
            "created_at": k.created_at,
            "chunk_count": chunk_count
        })

    return result

def create_knowledge_chunks(db: Session, knowledge_id: int, chunks: Sequence[dict]):
    """주어진 텍스트 청크와 벡터를 KnowledgeChunk 테이블에 저장"""
    for chunk in chunks:
        db.add(
            MSP_KnowledgeChunk(
                knowledge_id=knowledge_id,
                chunk_index=chunk["index"],
                chunk_text=chunk["text"],
                vector_memory=chunk["vector"],
            )
        )
    db.commit()

# 파일 경로 조회
def get_knowledge_by_id(db: Session, knowledge_id: int, user_id: int) -> str:
    """특정 파일 ID의 파일 경로를 반환한다."""
    knowledge = db.query(MSP_Knowledge).filter(MSP_Knowledge.id == knowledge_id).first()

    if knowledge is None:
        raise HTTPException(status_code=404, detail="Knowledge 조회 실패")

    if knowledge.user_id != user_id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    return knowledge.file_path


# chunk 조회
def get_chunk_by_id(db: Session, chunk_id: int) -> MSP_KnowledgeChunk:
    """지식 청크를 ID로 조회"""
    chunk = db.query(MSP_KnowledgeChunk).filter(MSP_KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="해당 청크가 없습니다.")
    return chunk
