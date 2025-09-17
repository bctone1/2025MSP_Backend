import core.config as config
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from models.user import User
from models.project import ProjectInfoBase, InfoList
from models.llm import ConversationLog, AIModel, Provider, ApiKey, ConversationSession
from models.agent import Agent, AgentStats, AgentSettings, AgentTypeRef
from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from langchain_service.llm.setup import get_llm
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from core.tools import mask_api_key
import os
import requests
from typing import List, Optional








##### 2025-08-18 초기 작성중
# crud/agent.py

# -----------------------------
# AgentTypeRef (lookup table)
# -----------------------------
def get_agent_types(db: Session) -> List[AgentTypeRef]:
    """에이전트 타입 목록 조회"""
    return db.execute(select(AgentTypeRef)).scalars().all()

# -----------------------------
# Agent 기본 CRUD
# -----------------------------
def create_agent(db: Session, id: str, name: str, type_code: str, avatar: Optional[str] = None,
                 description: Optional[str] = None, provider_id: Optional[int] = None,
                 model_id: Optional[int] = None, capabilities: Optional[List[str]] = None) -> Agent:
    """새 Agent 생성"""
    new_agent = Agent(
        id=id,
        name=name,
        type=type_code,   # FK → agent_types.code
        avatar=avatar,
        description=description,
        status="active",
        provider_id=provider_id,
        model_id=model_id,
        capabilities=capabilities or [],
        created_at=datetime.now(UTC)
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
    """Agent 단건 조회"""
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session) -> List[Agent]:
    """Agent 전체 조회"""
    return db.query(Agent).all()

def update_agent_status(db: Session, agent_id: str, status: str) -> Optional[Agent]:
    """Agent 상태 업데이트"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent:
        agent.status = status
        agent.last_active = datetime.utcnow()
        db.commit()
        db.refresh(agent)
    return agent

def delete_agent(db: Session, agent_id: str) -> bool:
    """Agent 삭제"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return False
    db.delete(agent)
    db.commit()
    return True

# -----------------------------
# Agent Stats 관리
# -----------------------------
def update_agent_stats(db: Session, agent_id: str, tasks_completed: int, success_rate: float):
    """Agent의 통계 업데이트"""
    stats = db.query(AgentStats).filter(AgentStats.agent_id == agent_id).first()
    if not stats:
        stats = AgentStats(agent_id=agent_id, tasks_completed=tasks_completed, success_rate=success_rate)
        db.add(stats)
    else:
        stats.tasks_completed = tasks_completed
        stats.success_rate = success_rate
    db.commit()
    return stats

# -----------------------------
# Agent Settings 관리
# -----------------------------
def update_agent_settings(db: Session, agent_id: str, max_tokens: int, temperature: float, search_depth: str):
    """Agent의 세부 설정 업데이트"""
    settings = db.query(AgentSettings).filter(AgentSettings.agent_id == agent_id).first()
    if not settings:
        settings = AgentSettings(agent_id=agent_id, max_tokens=max_tokens, temperature=temperature, search_depth=search_depth)
        db.add(settings)
    else:
        settings.max_tokens = max_tokens
        settings.temperature = temperature
        settings.search_depth = search_depth
    db.commit()
    return settings


