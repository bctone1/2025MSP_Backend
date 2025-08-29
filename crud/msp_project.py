from sqlalchemy.orm import Session
from models import MSP_Project
from datetime import datetime


# ✅ Create (프로젝트 생성)
def create_project(db: Session, user_id: int, name: str, category: str = None, description: str = None,
                   status: str = None, cost: str = None):
    new_project = MSP_Project(
        user_id=user_id,
        name=name,
        category=category,
        description=description,
        status=status,
        cost=cost,
        created_at=datetime.now()
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# ✅ Read (프로젝트 전체 조회)
def get_projects(db: Session, user_id: int):
    return db.query(MSP_Project).filter(MSP_Project.user_id == user_id).all()


# ✅ Read (프로젝트 단일 조회)
def get_project_by_id(db: Session, project_id: int):
    return db.query(MSP_Project).filter(MSP_Project.id == project_id).first()


# ✅ Update (프로젝트 수정)
def update_project(db: Session, project_id: int, name: str = None, category: str = None, description: str = None,
                   status: str = None, cost: str = None):
    project = db.query(MSP_Project).filter(MSP_Project.id == project_id).first()
    if not project:
        return None

    if name is not None:
        project.name = name
    if category is not None:
        project.category = category
    if description is not None:
        project.description = description
    if status is not None:
        project.status = status
    if cost is not None:
        project.cost = cost

    db.commit()
    db.refresh(project)
    return project


# ✅ Delete (프로젝트 삭제)
def delete_project(db: Session, project_id: int):
    project = db.query(MSP_Project).filter(MSP_Project.id == project_id).first()
    if not project:
        return None
    db.delete(project)
    db.commit()
    return project
