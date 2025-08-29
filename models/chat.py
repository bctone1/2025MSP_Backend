from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func, BigInteger, Table, JSON
from database.base import Base
from sqlalchemy.orm import relationship, backref


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
