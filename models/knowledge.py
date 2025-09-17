from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func, BigInteger,Table,JSON
from pgvector.sqlalchemy import Vector
from database.base import Base
from sqlalchemy.orm import relationship, backref
from models.associations import project_knowledge_association, session_knowledge_association  # 🔥 여기서 import

class MSP_Knowledge(Base):
    __tablename__ = "_msp_knowledge_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("_msp_user_table.user_id", ondelete="CASCADE"), nullable=False)
    origin_name = Column(String(255), nullable=False)
    file_path = Column(String(300), nullable=True)
    type = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    preview = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 역방향 관계
    user = relationship("MSP_USER", back_populates="knowledges")
    projects = relationship("MSP_Project",secondary=project_knowledge_association,back_populates="knowledges")
    sessions = relationship("MSP_Chat_Session",secondary=session_knowledge_association,back_populates="knowledges")
    chunks = relationship("MSP_KnowledgeChunk", back_populates="knowledge", cascade="all, delete-orphan")

class MSP_KnowledgeChunk(Base):
    __tablename__ = "_msp_knowledge_chunk_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_id = Column(Integer, ForeignKey("_msp_knowledge_table.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 몇 번째 청크인지 (순서 유지)
    chunk_text = Column(Text, nullable=False)  # 실제 잘린 텍스트
    vector_memory = Column(Vector(1536), nullable=True)  # 대화 임베딩 저장
    extra_data = Column(JSON, nullable=True)     # 추가 메타 정보 (토큰 수, 페이지, 문서 위치 등)

    # 역방향 관계
    knowledge = relationship("MSP_Knowledge", back_populates="chunks")


