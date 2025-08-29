from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func, BigInteger,Boolean
from database.base import Base
from sqlalchemy.orm import relationship



#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================
class MSP_USER(Base):
    __tablename__ = "_msp_user_table"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)  # 회원 고유 ID (PK)
    email = Column(String(255), unique=True, nullable=False)  # 로그인용 이메일
    password_hash = Column(Text, nullable=True)  # 비밀번호 해시
    name = Column(String(100), nullable=True)  # 사용자 이름/닉네임
    role = Column(String(20), nullable=True)  # 권한 (user/admin)
    terms_agreed = Column(Boolean, nullable=False, default=False)  # ✅ 약관 동의
    marketing_agreed = Column(Boolean, nullable=False, default=False)  # ✅ 마케팅 동의
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())  # 가입일
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())  # 수정일

    projects = relationship("MSP_Project",back_populates="user",cascade="all, delete-orphan")



#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================


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


