from sqlalchemy.orm import Session
from sqlalchemy import select
from models.project import *
from models.api import *

def create_new_project(db : Session, name : str, desc : str, category : str, model : str, user_email : str, provider : str):
    new_project = Project(
        user_email = user_email,
        project_name = name,
        category=category,
        description = desc,
        provider=provider,
        ai_model = model
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

def get_provider(db: Session):
    providers = db.execute(select(Provider.id, Provider.name, Provider.status, Provider.website, Provider.description)).all()

    return {
        "providers": [
            {
                "id" : p.id,
                "name": p.name,
                "status": p.status,
                "website": p.website,
                "description": p.description
            } for p in providers
        ]
    }

def delete_session(db: Session, session_id : str):
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()

def delete_infobase(db: Session, infobase_id : int):
    file = db.query(ProjectInfoBase).filter(ProjectInfoBase.id == infobase_id).first()
    if file:
        db.delete(file)
        db.commit()
