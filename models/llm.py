from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Float
from database.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector

class Provider(Base):
    __tablename__ = "provider_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(String(50))
    website = Column(String(255))
    description = Column(Text)

class ApiKey(Base):
    __tablename__ = "api_key_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("provider_table.id", ondelete="CASCADE"), nullable=False)
    provider_name = Column(String(255), ForeignKey("provider_table.name", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False)
    api_key = Column(Text, nullable=False)
    status = Column(String(50))
    create_at = Column(TIMESTAMP, default=func.current_timestamp())
    usage_limit = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)

    provider = relationship("Provider", backref="api_keys", foreign_keys=[provider_id])
    user = relationship("User", backref="api_keys")

class ConversationSession(Base):
    __tablename__ = "conversation_session"

    id = Column(String(255), primary_key=True)
    session_title = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey('project_table.project_id', ondelete='CASCADE'))
    user_email = Column(String(255), ForeignKey('user_table.email', ondelete='CASCADE'))
    register_at = Column(TIMESTAMP, default=func.current_timestamp())
    project = relationship("Project", backref="conversation_sessions")
    user = relationship("User", backref="conversation_sessions")

class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("conversation_session.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), ForeignKey("user_table.email", ondelete="CASCADE"), nullable=False)
    message_role = Column(String(255), nullable=False)
    conversation = Column(Text, nullable=False)
    vector_memory = Column(Vector(1536), nullable=True)  # 벡터 크기 1536의 배열로 저장
    request_at = Column(TIMESTAMP, default=func.current_timestamp())
    case = Column(String(50))

    session = relationship(
        "ConversationSession",
        backref=backref("logs", passive_deletes=True)
    )
    project = relationship("Project", backref="logs")
    user = relationship("User", backref="logs")

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)

    provider_id = Column(Integer, ForeignKey('provider_table.id', ondelete='CASCADE'), nullable=False)
    provider_name = Column(String(255), ForeignKey('provider_table.name', ondelete='CASCADE'), nullable=False)
    provider = relationship('Provider', backref='ai_models', foreign_keys=[provider_id])