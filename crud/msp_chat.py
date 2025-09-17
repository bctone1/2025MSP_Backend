from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, text

from langchain_service.embedding.get_vector import text_to_vector
from models import *
from datetime import datetime, UTC


def get_similarity_search_by_knowledge_ids(
        db: Session,
        knowledge_ids: list[int],
        user_input: str,
        top_k: int = 3
):
    # 1. 사용자 입력을 벡터로 변환
    user_input_vector = text_to_vector(user_input)  # numpy array
    user_input_vector = user_input_vector.tolist()  # list

    # 백터를 제외한 데이터 출력
    # stmt = text("""
    # SELECT id, knowledge_id, chunk_index, chunk_text, extra_data,
    #        vector_memory <=> CAST(:query_vector AS vector) AS similarity
    # FROM _msp_knowledge_chunk_table
    # WHERE knowledge_id = ANY(:knowledge_ids)
    # ORDER BY similarity ASC
    # LIMIT :top_k
    # """)

    stmt = text("""
        SELECT  chunk_text,
               vector_memory <=> CAST(:query_vector AS vector) AS similarity
        FROM _msp_knowledge_chunk_table
        WHERE knowledge_id = ANY(:knowledge_ids)
        ORDER BY similarity ASC
        LIMIT :top_k
        """)

    rows = db.execute(stmt, {
        "knowledge_ids": knowledge_ids,
        "query_vector": user_input_vector,
        "top_k": top_k
    }).fetchall()

    # 3. dict 리스트 형태로 반환
    return [dict(r._mapping) for r in rows]


def get_sessions_by_user(db: Session, user_id: int):
    sessions = (
        db.query(MSP_Chat_Session)
        .options(joinedload(MSP_Chat_Session.project))  # 프로젝트 미리 로드
        .filter(MSP_Chat_Session.user_id == user_id)
        .order_by(desc(MSP_Chat_Session.id))
        .all()
    )

    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "user_id": s.user_id,
            "title": s.title,
            "project_id": s.project_id,  # project_id도 포함
            "project_name": s.project.name if s.project else None,  # project가 없으면 None
            "created_at": s.created_at,
            "preview": s.preview
        })

    return result


def create_session(
        db: Session,
        user_id: int,
        title: str,
        project_id: int = None,
        preview: str = None,
) -> MSP_Chat_Session:
    """
    새로운 채팅 세션을 생성하고 DB에 저장하는 함수
    """
    new_session = MSP_Chat_Session(
        user_id=user_id,
        project_id=project_id,
        title=title,
        preview=preview,
        created_at=datetime.now(UTC)
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)  # 새로 생성된 id 값 등을 반영
    return new_session


# def get_messages_by_session(db: Session, session_id: int):
#     return (
#         db.query(MSP_Message)
#         .filter(MSP_Message.session_id == session_id)
#         .order_by(MSP_Message.id)  # id 기준 내림차순 정렬
#         .all()
#     )

def get_messages_by_session(db: Session, session_id: int):
    return (
        db.query(
            MSP_Message.id,
            MSP_Message.session_id,
            MSP_Message.role,
            MSP_Message.content,
            MSP_Message.extra_data,
            MSP_Message.created_at
        )
        .filter(MSP_Message.session_id == session_id)
        .order_by(MSP_Message.id)
        .all()
    )


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
