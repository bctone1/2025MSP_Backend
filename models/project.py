from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from database.base import Base
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector


# =======================================
# Project (프로젝트 메타 정보)
# - user_table.email FK 참조
# - 프로젝트 기본 속성 관리
# =======================================
class Project(Base):
    __tablename__ = "project_table"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)
    project_name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    provider = Column(String(255))
    ai_model = Column(String(255))

    # 관계: User ↔ Project (1:N)
    user = relationship("User", back_populates="projects")    ## 관례상 다수가 되는 projects로 작명


# =======================================
# ProjectInfoBase (프로젝트 파일/지식베이스 메타)
# - project_table.project_id FK 참조
# - user_table.email FK 참조
# - 프로젝트에 업로드된 파일 관리
# =======================================
class ProjectInfoBase(Base):
    __tablename__ = "project_info_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255))
    file_url = Column(Text, nullable=True)
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 관계: Project ↔ ProjectInfoBase (1:N)
    project = relationship("Project", backref="info")
    # 관계: User ↔ ProjectInfoBase (1:N)
    user = relationship("User", backref="project_info")


# =======================================
# InfoList (세부 지식 단위 + 벡터 임베딩)
# - project_info_base.id FK 참조
# - pgvector.Vector(1536)로 임베딩 저장
# =======================================
class InfoList(Base):
    __tablename__ = "info_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    infobase_id = Column(Integer, ForeignKey("project_info_base.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text)
    vector_memory = Column(Vector(1536))
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 관계: ProjectInfoBase ↔ InfoList (1:N)
    infobase = relationship(
        "ProjectInfoBase",
        backref=backref("info_list", passive_deletes=True)
    )
