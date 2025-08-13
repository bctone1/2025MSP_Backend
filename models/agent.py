from sqlalchemy import UniqueConstraint, Column, Integer, String, Text, DateTime, ForeignKey, Float, Index
from database.base import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector

# AgentType lookup Table
class AgentTypeRef(Base):
    __tablename__ = "agent_types"
    code = Column(String(50), primary_key=True)
    label = Column(String(100))
    description = Column(Text)

    __table_args__ = (
        UniqueConstraint('label', name='uq_agent_types_label'),
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key = True)
    name = Column(String(255))
    type = Column(String(50), ForeignKey('agent_types.code'))    # FK로 연결
    avatar = Column(String)
    description = Column(Text)
    status = Column(String, default = 'active')
    model = Column(String(255))
    capabilities = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())     # 현재값 추가
    last_active = Column(DateTime)

    # 여기 추가 provider_id 로 사용. 왜냐하면 provider_table에 id가 PK임.
    # ai_models 는 provider_id를 FK로 갖고 있음.
    provider_id = Column(Integer, ForeignKey('provider_table.id'), nullable=True)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=True)
    # provider_name = Column(String(255), ForeignKey('provider_table.name'), nullable=True)
    # model = Column(String(255))


    # 관계 설정: Agent.agent_type 로 접근 가능
    agent_type = relationship(
    "AgentTypeRef",
    backref=backref("agents", lazy="dynamic"),
    lazy="joined",
)



class AgentStats(Base):
    __tablename__ = 'agent_stats'

    agent_id = Column(String, ForeignKey('agents.id'), primary_key=True)
    tasks_completed = Column(Integer)
    success_rate = Column(Float)

    agent = relationship("Agent", backref=backref("stats", uselist=False))

class AgentSettings(Base):
    __tablename__ = 'agent_settings'
    agent_id = Column(String, ForeignKey('agents.id'), primary_key=True)
    max_tokens = Column(Integer)
    temperature = Column(Float)
    search_depth = Column(String(255))
    agent = relationship("Agent", backref=backref("settings", uselist=False))

