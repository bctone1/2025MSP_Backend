from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from database.base import Base
from sqlalchemy.orm import relationship
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
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    project = relationship("Project", backref="info")
    user = relationship("User", backref="project_info")

class InfoList(Base):
    __tablename__ = "info_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    infobase_id = Column(Integer, ForeignKey("project_info_base.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    vector_memory = Column(Vector(1536))
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    infobase = relationship("ProjectInfoBase", backref="info_list")
