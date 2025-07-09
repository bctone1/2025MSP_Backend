from sqlalchemy.orm import Session
from sqlalchemy import select
from models.project import *
from models.user import User
from models.llm import *
from typing import List

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

def select_and_delete_infobase(db: Session, project_id : int, file_name : str):
    file_url = 'saved_file/' + file_name
    files = db.query(ProjectInfoBase).filter(ProjectInfoBase.project_id == project_id, ProjectInfoBase.file_url == file_url).all()
    for file in files:
        db.delete(file)
        db.commit()

def delete_project(db: Session, project_ids:List[int]):
    db.query(Project).filter(Project.project_id.in_(project_ids)).delete(synchronize_session=False)
    db.commit()
    return "deleted"

def get_project_list(db : Session, email : str):
    user_role = db.query(User.role).filter(User.email == email).first()[0]
    if user_role.lower() == "admin":
        total_list = db.query(Project).order_by(Project.project_id.desc()).all()
        return total_list
    else:
        personal_list = (db.query(Project).filter(Project.user_email.ilike(email.lower())).
                         order_by(Project.project_id.desc()).
                         all())
        return personal_list