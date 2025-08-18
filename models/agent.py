from sqlalchemy import UniqueConstraint, Column, Integer, String, Text, DateTime, ForeignKey, Float, Index
from database.base import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector


# =======================================
# AgentTypeRef (에이전트 타입 레퍼런스 테이블)
# - research / coding / analysis / writing 등 코드 정의
# - label 은 UNIQUE 제약
# =======================================
class AgentTypeRef(Base):
    __tablename__ = "agent_types"

    code = Column(String(50), primary_key=True)   # 예: "research"
    label = Column(String(100))                   # UI 표시용
    description = Column(Text)

    __table_args__ = (
        UniqueConstraint('label', name='uq_agent_types_label'),
    )


# =======================================
# Agent (실제 에이전트 인스턴스)
# - FK: type → AgentTypeRef.code
# - FK: provider_id → Provider.id
# - FK: model_id → AIModel.id
# =======================================
class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    type = Column(String(50), ForeignKey('agent_types.code'))   # 에이전트 타입 참조
    avatar = Column(String)
    description = Column(Text)
    status = Column(String, default='active')
    model = Column(String(255))
    capabilities = Column(ARRAY(String))                       # 수행 가능한 기능 리스트
    created_at = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime)

    # Provider / Model 참조 (연결용 FK)
    provider_id = Column(Integer, ForeignKey('provider_table.id'), nullable=True)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=True)

    # 관계: Agent ↔ AgentTypeRef (N:1)
    agent_type = relationship(
        "AgentTypeRef",
        backref=backref("agents", lazy="dynamic"),
        lazy="joined",
    )


# =======================================
# AgentStats (에이전트 실행 통계)
# - FK: agent_id → Agent.id
# =======================================
class AgentStats(Base):
    __tablename__ = 'agent_stats'

    agent_id = Column(String, ForeignKey('agents.id'), primary_key=True)
    tasks_completed = Column(Integer)   # 완료된 작업 수
    success_rate = Column(Float)        # 성공률 (완료/전체)

    # 관계: Agent ↔ AgentStats (1:1)
    agent = relationship("Agent", backref=backref("stats", uselist=False))


# =======================================
# AgentSettings (에이전트 설정값)
# - FK: agent_id → Agent.id
# =======================================
class AgentSettings(Base):
    __tablename__ = 'agent_settings'

    agent_id = Column(String, ForeignKey('agents.id'), primary_key=True)
    max_tokens = Column(Integer)
    temperature = Column(Float)
    search_depth = Column(String(255))

    # 관계: Agent ↔ AgentSettings (1:1)
    agent = relationship("Agent", backref=backref("settings", uselist=False))
