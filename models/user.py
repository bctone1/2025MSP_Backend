from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from database.base import Base
from sqlalchemy.orm import relationship


# =======================================
# 👤 User (사용자 계정 정보)
# - 프로젝트, API Key, 세션 등 모든 엔티티의 기준이 되는 root 테이블
# - email, phone_number는 UNIQUE 제약
# =======================================
class User(Base):
    __tablename__ = "user_table"

    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)   # 로그인 ID
    password = Column(Text, nullable=False)                   # bcrypt 해시 저장
    name = Column(String(100), nullable=False)

    # 권한 / 그룹
    role = Column(String(50))      # 예: admin / normalUser
    group = Column(String(100))    # 소속 그룹

    # 메타 정보
    register_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    phone_number = Column(String(20), unique=True)

    # 관계: User ↔ Project (1:N)
    projects = relationship("Project", back_populates="user", lazy="dynamic")
