from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database.base import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    collection_name = Column(String(255), nullable=False)
    document_id = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
