from sqlalchemy.orm import Session
from models.project import Project

def create_project(
    db: Session,
    project_name: str,
    start_date: str,
    end_date: str,
    description: str,
    requirements: str,
    model_setting: str,
    num_of_member: int,
    user_email: str,
) -> Project:
    """
    프로젝트 데이터를 데이터베이스에 추가하는 함수.
    """
    new_project = Project(
        project_name=project_name,
        start_date=start_date,
        end_date=end_date,
        description=description,
        requirements=requirements,
        model_setting=model_setting,
        num_of_member_=num_of_member,
        user_email=user_email,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
