from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func, BigInteger,Table,JSON
from database.base import Base
from sqlalchemy.orm import relationship, backref
from models.associations import project_knowledge_association  # 🔥 여기서 import

class MSP_Knowledge(Base):
    __tablename__ = "_msp_knowledge_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    size = Column(String(50), nullable=True)
    uploaded = Column(String(100), nullable=True)

    # 역방향 관계
    projects = relationship("MSP_Project",secondary=project_knowledge_association,back_populates="knowledge")


