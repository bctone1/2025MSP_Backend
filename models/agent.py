from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from database.base import Base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from pgvector.sqlalchemy import Vector

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key = True)
    name = Column(String(255))
    type = Column(String(50))
    avatar = Column(String)
    description = Column(Text)
    status = Column(String, default = 'active')
    model = Column(String(255))
    capabilities = Column(ARRAY(String))
    created_at = Column(DateTime)
    last_active = Column(DateTime)



class AgentStats(Base):
    __tablename__ = 'agent_stats'

    agent_id = Column(String, ForeignKey('agents.id'), primary_key=True)
    tasksCompleted = Column(Integer)
    successRate = Column(Float)

class AgentSettings(Base):
    __tablename__ = 'agent_settings'

    maxTokens = Column(Integer)
    temperature = Column(Float)
    searchDepth = Column(String(255))