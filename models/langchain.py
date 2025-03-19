from sqlalchemy import Column, ForeignKey, Integer, Text, String, JSON, TIMESTAMP
from pgvector.sqlalchemy import Vector
from database.base import Base
from sqlalchemy.sql import func
'''
class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    collection_name = Column(String(255), nullable=False)
    document_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    doc_metadata = Column(JSON, nullable=True)
    embedding = Column(Vector(1536), nullable=True)

class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=True)
    type = Column(String(50), nullable=False)  # 'human' or 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    additional_kwargs = Column(JSON, nullable=True)

class AgentAction(Base):
    __tablename__ = 'agent_actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=True)
    action = Column(String(255), nullable=False)
    action_input = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)'''