from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, JSON, TIMESTAMP, func
from database.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA
from pgvector.sqlalchemy import Vector


class User(Base):
    __tablename__ = "user_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50))
    group = Column(String(100))
    register_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    projects = relationship("Project", back_populates="user", lazy="dynamic")

class Project(Base):
    __tablename__ = "project_table"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)
    project_name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    provider = Column(String(255))
    ai_model = Column(String(255))

    user = relationship("User", back_populates="projects")

class ProjectInfoBase(Base):
    __tablename__ = "project_info_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)
    file_url = Column(Text, nullable=True)
    file = Column(BYTEA, nullable=True)  # 파일을 BYTEA 형식으로 저장
    vector_memory = Column(ARRAY(Integer), nullable=True)  # 벡터 크기 1536의 배열로 저장
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 외래 키 관계 설정
    project = relationship("Project", backref="info")
    user = relationship("User", backref="project_info")

'''   
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
'''