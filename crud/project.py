from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import MSP_Chat_Session
from models.project import *
from models.user import User
from models.llm import *
from typing import List, Optional
from sqlalchemy.orm import joinedload


def create_project(
    db: Session,
    user_id: int,
    name: str,
    category: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    cost: Optional[str] = None,
) -> MSP_Project:
    new_project = MSP_Project(
        user_id=user_id,
        name=name,
        category=category,
        description=description,
        status=status,
        cost=cost,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

#
# def get_projects_by_user(db: Session, user_id: int) -> List[MSP_Project]:
#     return db.query(MSP_Project).filter(MSP_Project.user_id == user_id).all()

def get_projects_by_user(db: Session, user_id: int) -> List[MSP_Project]:
    return (
        db.query(MSP_Project)
        .options(
            # chat_sessions와 그 안의 messages를 함께 로드
            joinedload(MSP_Project.chat_sessions).joinedload(MSP_Chat_Session.messages),
            # project와 연결된 knowledge
            joinedload(MSP_Project.knowledges)
        )
        .filter(MSP_Project.user_id == user_id)
        .order_by(desc(MSP_Project.id))
        .all()
    )


def serialize_project(p: MSP_Project):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "status": p.status,
        "cost": p.cost,
        "conversations": [
            {
                "id": s.id,
                "title": s.title or "",
                # "status": s.status or "",
                "date": getattr(s, "created_at", None).strftime("%Y-%m-%d %H:%M")
                        if getattr(s, "created_at", None) else None,
                "preview": s.preview or "",
                "messages": len(s.messages) if s.messages is not None else 0
            }
            for s in p.chat_sessions or []
        ],
        "knowledge": [
            {
                "id": k.id,
                "name": k.name or "",
                "type": k.type or "",
                "size": k.size,
                "uploaded": getattr(k, "uploaded_at", None).strftime("%Y-%m-%d")
                            if getattr(k, "uploaded_at", None) else None
            }
            for k in p.knowledges or []
        ]
    }
