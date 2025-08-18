from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Float
from database.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector


# =======================================
# Provider (AI 제공자 정보)
# - 예: OpenAI, Anthropic, Google 등
# - name 은 UNIQUE
# =======================================
class Provider(Base):
    __tablename__ = "provider"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(String(50))
    website = Column(String(255))
    description = Column(Text)


# =======================================
# ApiKey (사용자별 API Key 관리)
# - FK: provider_id → Provider.id
# - FK: provider_name → Provider.name
# - FK: user_id → User.id
# =======================================
class ApiKey(Base):
    __tablename__ = "api_key"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("provider_table.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), unique=True, nullable=False)

    api_key = Column(Text, nullable=False)
    status = Column(String(50))
    create_at = Column(TIMESTAMP, default=func.current_timestamp())
    usage_limit = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)

    # 관계: Provider ↔ ApiKey (1:N)
    provider = relationship("Provider", backref="api_keys", foreign_keys=[provider_id])
    # 관계: User ↔ ApiKey (1:N)
    user = relationship("User", backref="api_keys")


# =======================================
# ConversationSession (대화 세션 메타)
# - FK: project_id → Project.project_id
# - FK: user_email → User.email
# =======================================
class ConversationSession(Base):
    __tablename__ = "conversation_session"

    id = Column(String(255), primary_key=True)
    session_title = Column(String(255), nullable=False)

    project_id = Column(Integer, ForeignKey('project_table.project_id', ondelete='CASCADE'))
    user_email = Column(String(255), ForeignKey('user_table.email', ondelete='CASCADE'))
    register_at = Column(TIMESTAMP, default=func.current_timestamp())

    # 관계: Project ↔ ConversationSession (1:N)
    project = relationship("Project", backref="conversation_sessions")
    # 관계: User ↔ ConversationSession (1:N)
    user = relationship("User", backref="conversation_sessions")


# =======================================
# ConversationLog (대화 로그)
# - FK: session_id → ConversationSession.id
# - FK: project_id → Project.project_id
# - FK: user_email → User.email
# - pgvector.Vector(1536) 로 임베딩 저장
# =======================================
class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("conversation_session.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)

    message_role = Column(String(255), nullable=False)   # user / assistant / system
    conversation = Column(Text, nullable=False)
    vector_memory = Column(Vector(1536), nullable=True)  # 대화 임베딩 저장
    request_at = Column(TIMESTAMP, default=func.current_timestamp())
    case = Column(String(50))

    # 관계: ConversationSession ↔ ConversationLog (1:N)
    session = relationship(
        "ConversationSession",
        backref=backref("logs", passive_deletes=True)
    )
    # 관계: Project ↔ ConversationLog (1:N)
    project = relationship("Project", backref="logs")
    # 관계: User ↔ ConversationLog (1:N)
    user = relationship("User", backref="logs")


# =======================================
# AIModel (AI 모델 정보)
# - FK: provider_id → Provider.id
# - FK: provider_name → Provider.name
# =======================================
class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), unique=True, nullable=False)

    provider_id = Column(Integer, ForeignKey('provider_table.id', ondelete='CASCADE'), unique=True, nullable=False)
    provider_name = Column(String(255), ForeignKey('provider_table.name', ondelete='CASCADE'), nullable=False)

    # 관계: Provider ↔ AIModel (1:N)
    provider = relationship('Provider', backref='ai_models', foreign_keys=[provider_id])
