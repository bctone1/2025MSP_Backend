from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func, BigInteger,Table,JSON
from database.base import Base
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector




#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================

# 중간 테이블 (프로젝트 ↔ 지식 연결)
project_knowledge_association = Table(
    "_msp_project_knowledge_association",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("_msp_project_table.id", ondelete="CASCADE"), primary_key=True),
    Column("knowledge_id", Integer, ForeignKey("_msp_knowledge_table.id", ondelete="CASCADE"), primary_key=True)
)


class MSP_Project(Base):
    __tablename__ = "_msp_project_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("_msp_user_table.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)
    cost = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("MSP_USER",back_populates="projects")

    # 관계 설정
    chat_sessions = relationship("MSP_Chat_Session", back_populates="project", cascade="all, delete-orphan")

    # ✅ 다대다 관계 (프로젝트 삭제 시 연결만 삭제됨, 지식은 보존됨)
    knowledge = relationship(
        "MSP_Knowledge",
        secondary=project_knowledge_association,
        back_populates="projects"
    )

class MSP_Chat_Session(Base):
    __tablename__ = "_msp_chat_session_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("_msp_project_table.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=True)
    date = Column(String(100), nullable=True)  # "2시간 전", "어제" → 문자열 저장 (또는 TIMESTAMP로 바꿀 수도 있음)
    preview = Column(Text, nullable=True)
    message_count = Column(Integer, default=0)
    # 관계 역방향
    project = relationship("MSP_Project", back_populates="chat_sessions")
    messages = relationship("MSP_Message", back_populates="session", cascade="all, delete-orphan")

class MSP_Message(Base):
    __tablename__ = "_msp_message_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 어떤 세션에 속한 메시지인지
    session_id = Column(Integer, ForeignKey("_msp_chat_session_table.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    # 첨부 파일, 이미지, JSON 등 멀티모달 확장 고려
    extra_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 관계
    session = relationship("MSP_Chat_Session", back_populates="messages")



class MSP_Knowledge(Base):
    __tablename__ = "_msp_knowledge_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    uploaded = Column(String(100), nullable=True)

    # 역방향 관계
    projects = relationship(
        "MSP_Project",
        secondary=project_knowledge_association,
        back_populates="knowledge"
    )




#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================



# =======================================
# Project (프로젝트 메타 정보)
# - 프로젝트 기본 속성 관리
# =======================================
class Project(Base):
    __tablename__ = "project_table"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("user_table.id", ondelete="RESTRICT"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True, index=True)
    project_name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 관계: User ↔ Project (1:N)
    user = relationship("User", back_populates="projects")    ## 관례상 다수가 되는 projects로 작명
    model = relationship("AIModel", back_populates="projects")
    info_bases = relationship("ProjectInfoBase", back_populates="project", cascade="all,delete")  # 명시


# =======================================
# ProjectInfoBase (프로젝트 파일/지식베이스 메타)
# - project_table.project_id FK 참조
# - 프로젝트에 업로드된 파일 관리
# =======================================
class ProjectInfoBase(Base):
    __tablename__ = "project_info_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"),
                                 nullable=True, index=True)
    file_name = Column(String(255))
    file_url = Column(Text, nullable=True)
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 관계: Project ↔ ProjectInfoBase (1:N)
    project = relationship("Project", backref="info")
    uploader = relationship("User", backref="uploaded_info_bases")

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
    infobase_id = Column(Integer, ForeignKey("project_info_base.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text)
    vector_memory = Column(Vector(1536))
    upload_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 관계: ProjectInfoBase ↔ InfoList (1:N)
    infobase = relationship(
        "ProjectInfoBase",
        backref=backref("info_list", passive_deletes=True))

