import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from models.project import Project

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