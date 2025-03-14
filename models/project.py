from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, JSON
from database.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector


class User(Base):
    __tablename__ = 'user_table'

    email = Column(String, primary_key=True, index=True)
    pw = Column(String, nullable=False)
    role = Column(String, nullable=False)
    group = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    skills = Column(ARRAY(Text), nullable=True)
    register_at = Column(Date, nullable=True)

class Project(Base):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(String, nullable=True)
    model_setting = Column(String, nullable=False)
    num_of_member_ = Column(Integer, nullable=True)
    user_email = Column(String, ForeignKey('user_table.email'), nullable=True)

    # 관계 설정: 프로젝트는 특정 사용자를 참조할 수 있음
    user = relationship("User", back_populates="projects")
    table_data = relationship("TableData", back_populates="project")
    api_data = relationship("APITable", back_populates="project")

# User 모델에 Project와의 관계를 설정
User.projects = relationship("Project", back_populates="user")

class Requirements(Base):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    definition = Column(Text, nullable=True)

    # 관계 설정: 요구 사항은 특정 프로젝트와 관련됨
    project = relationship("Project", back_populates="requirements")

# Project 모델에 Requirements와의 관계를 설정
Project.requirements = relationship("Requirements", back_populates="project")


class SystemSetting(Base):
    __tablename__ = 'systemSetting'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    definition = Column(Text, nullable=True)

    project = relationship("Project", back_populates="system_settings")

# Project 모델에 SystemSetting과의 관계 설정
Project.system_settings = relationship("SystemSetting", back_populates="project")

class TableData(Base):
    __tablename__ = 'tabledata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    table_name = Column(String(255), nullable=False)
    columns = Column(ARRAY(Text), nullable=True)
    description = Column(Text, nullable=True)

    # Project와의 관계 설정 (각 프로젝트는 여러 개의 TableData를 가질 수 있음)
    project = relationship("Project", back_populates="table_data")

class APITable(Base):
    __tablename__ = 'apitable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    api_name = Column(String(255), nullable=False)
    apidata = Column(JSON, nullable=True)  # JSON 필드
    description = Column(Text, nullable=True)

    # Project와의 관계 설정
    project = relationship("Project", back_populates="api_data")
