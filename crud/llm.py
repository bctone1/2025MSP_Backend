import core.config as config
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from models.user import User
from models.project import ProjectInfoBase, InfoList
from models.llm import ConversationLog, AIModel, Provider, ApiKey, ConversationSession
from sqlalchemy import select
from sqlalchemy.sql import func
from langchain_service.llm.setup import get_llm
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from core.tools import mask_api_key
import os
import requests

# ===============================
# 파일 업로드 & Info 저장 관련
# ===============================

def upload_file(db: Session, project: int, email: str, url: str, name: str):
    """
    새 파일을 project_info_base 테이블에 업로드 기록 저장
    - FK: project_id → project_table.project_id
    - FK: user_email → user.email
    """
    try:
        new_file = ProjectInfoBase(
            project_id=project,
            user_email=email,
            file_url=url,
            upload_at=datetime.now(UTC),
            file_name=name
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file.id
    except Exception as e:
        db.rollback()
        raise e


def save_info(db: Session, infobase_id: int, content: str, vector_memory: list):
    """
    업로드된 파일에 대한 추가 정보 저장 (info_list 테이블)
    - FK: infobase_id → project_info_base.id
    """
    try:
        new_info = InfoList(
            infobase_id=infobase_id,
            content=content,
            vector_memory=vector_memory,
            upload_at=datetime.now(UTC)
        )
        db.add(new_info)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


# ===============================
# 대화(Conversation) 관련
# ===============================

def add_message(db: Session, session_id: str, project_id: int, user_email: str,
                message_role: str, conversation: str, vector_memory: list, case: str):
    """
    새 메시지를 conversation_logs 테이블에 추가
    - FK: session_id → conversation_session.id
    - FK: project_id → project_table.project_id
    - FK: user_email → user_table.email
    """
    try:
        vector = np.array(vector_memory).flatten()
        new_message = ConversationLog(
            session_id=session_id,
            project_id=project_id,
            user_email=user_email,
            message_role=message_role,
            conversation=conversation,
            vector_memory=vector,
            request_at=datetime.now(UTC),
            case=case
        )
        db.add(new_message)
        db.commit()
        return {"message": "Message saved successfully!", "request_at": new_message.request_at}
    except Exception as e:
        db.rollback()
        raise e


def get_chat_history(db: Session, session_id: int):
    """
    특정 세션의 전체 대화 기록 + info_list 내용까지 불러오기
    """
    history_messages = []
    stmt = select(ConversationLog).where(
        ConversationLog.session_id == session_id
    ).order_by(ConversationLog.request_at)
    results = db.execute(stmt).scalars().all()
    if not results:
        return history_messages

    # 세션에 연결된 project_id로 info_list까지 함께 조회
    project_id = results[0].project_id
    info_base_stmt = select(ProjectInfoBase).where(ProjectInfoBase.project_id == project_id)
    info_base_result = db.execute(info_base_stmt).scalar()
    if info_base_result:
        info_id = info_base_result.id
        info_list_stmt = select(InfoList).where(
            InfoList.infobase_id == info_id
        ).order_by(InfoList.upload_at)
        infos = db.execute(info_list_stmt).scalars().all()

        # system role 로 info 내용 삽입
        for info in infos:
            history_messages.append({
                'message_role': "System",
                'conversation': info.content,
                'vector_memory': info.vector_memory
            })

    # 실제 유저/AI 메시지 추가
    for msg in results:
        history_messages.append({
            'message_role': msg.message_role,
            'conversation': msg.conversation,
            'vector_memory': msg.vector_memory
        })
    return history_messages


# ===============================
# 모델 & Provider 관련
# ===============================

def get_model_list(db: Session):
    """모든 AI 모델 목록 조회"""
    models = db.execute(
        select(AIModel.id, AIModel.model_name, AIModel.provider_id, AIModel.provider_name)
    ).all()
    return {
        "models": [
            {
                "id": m.id,
                "model_name": m.model_name,
                "provider_id": m.provider_id,
                "provider_name": m.provider_name,
            } for m in models
        ]
    }


def delete_model(db: Session, model_id: int):
    """AI 모델 삭제"""
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    db.delete(model)
    db.commit()
    return "Deleted"


def delete_provider(db: Session, provider_id: int):
    """
    Provider 삭제 시 연결된 모델/ApiKey도 함께 삭제
    - FK 연쇄관계 때문에 직접 삭제 후 Provider 제거
    """
    ai_models = db.query(AIModel).filter(AIModel.provider_id == provider_id).all()
    for model in ai_models:
        db.delete(model)
    api_keys = db.query(ApiKey).filter(ApiKey.provider_id == provider_id).all()
    for key in api_keys:
        db.delete(key)
    db.commit()
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    db.delete(provider)
    db.commit()
    return "Deleted"


def add_provider(db: Session, name: str, status: str, website: str, description: str):
    """새 Provider 추가"""
    new_provider = Provider(
        name=name,
        status=status,
        website=website,
        description=description
    )
    db.add(new_provider)
    db.commit()


def add_model(db: Session, provider_name: str, name: str):
    """Provider 이름 기반으로 새 모델 추가"""
    provider_id = db.query(Provider.id).filter(Provider.name == provider_name).scalar()
    new_model = AIModel(
        model_name=name,
        provider_id=provider_id,
        provider_name=provider_name
    )
    db.add(new_model)
    db.commit()


def change_model(db: Session, id: int, provider_name: str, name: str):
    """기존 모델 정보 수정"""
    provider_id = db.query(Provider.id).filter(Provider.name == provider_name).scalar()
    model = db.query(AIModel).filter(AIModel.id == id).first()
    if model:
        model.model_name = name
        model.provider_id = provider_id
        model.provider_name = provider_name
        db.commit()
        db.refresh(model)
        return model
    else:
        return None


# ===============================
# API Key 관리
# ===============================

def get_api_keys(db: Session, email: str):
    """
    특정 유저(email)의 API Key 목록 조회
    - FK: user_id → user_table.id
    """
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return {"api_keys": [], "message": "please enter your apikey"}

    keys = db.execute(
        select(ApiKey).where(ApiKey.user_id == user.id)
    ).scalars().all()

    return {
        "api_keys": [
            {
                "id": k.id,
                "provider_id": k.provider_id,
                "provider_name": k.provider_name,
                "user_id": k.user_id,
                "api_key": mask_api_key(k.api_key),
                "status": k.status,
                "create_at": k.create_at,
                "usage_limit": k.usage_limit,
                "usage_count": k.usage_count
            } for k in keys
        ]
    }


def get_api_key(db: Session, user_email: str, provider: str):
    """
    특정 유저/Provider 조합으로 실제 API Key 반환
    - OpenAI, Anthropic 같은 경우 하드코딩된 provider_id를 사용 중
    """
    user = db.query(User).filter(User.email == user_email).first()
    user_id = user.id

    if provider == 'openai':
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id == 4).first()
        if not api:
            return None
        return api.api_key

    elif provider == "anthropic":
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id == 2).first()
        if not api:
            return None
        elif api.api_key == 'Default API Key':
            return config.DEFAULT_API_KEY
        return api.api_key


# ===============================
# 세션 관리
# ===============================

def get_session(db: Session, email: str):
    """유저의 세션 목록 + 메시지 개수 반환"""
    subquery = (
        db.query(
            ConversationLog.session_id,
            func.count().label("messages")
        )
        .filter(ConversationLog.message_role != 'user')
        .group_by(ConversationLog.session_id)
        .subquery()
    )

    query = (
        db.query(
            ConversationSession,
            func.coalesce(subquery.c.messages, 0).label("messages")
        )
        .outerjoin(subquery, ConversationSession.id == subquery.c.session_id)
        .filter(ConversationSession.user_email == email)
        .order_by(ConversationSession.id.desc())
    )
    result = []
    for session, messages in query.all():
        session_dict = session.__dict__.copy()
        session_dict['messages'] = messages
        result.append(session_dict)
    return result


def add_new_session(db: Session, id: str, project_id: int, session_title: str, user_email: str):
    """새 대화 세션 생성"""
    already_exists = db.query(ConversationSession).filter(ConversationSession.id == id).first()
    if already_exists:
        return "already_exist"
    new_session = ConversationSession(
        id=id,
        session_title=session_title,
        register_at=datetime.utcnow(),
        project_id=project_id,
        user_email=user_email
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def change_session_title(db: Session, session_id: str, content: str):
    """세션 제목 변경"""
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    session.session_title = content
    db.commit()
    db.refresh(session)
    return session


# ===============================
# 유틸리티 함수
# ===============================

async def verify_api_key(provider: str, api_key: str, model: str = None):
    """실제 API Key 유효성 체크 (LLM 호출 테스트)"""
    try:
        provider = provider.lower()
        llm = get_llm(provider=provider, model=model, api_key=api_key)
        prompt = ChatPromptTemplate.from_messages([("user", "Say hello")])
        chain = prompt | llm
        response = await chain.ainvoke({})
        if not response:
            raise ValueError("Empty response received.")
    except Exception as e:
        raise ValueError(f"API Key 검증 실패: {str(e)}")
    return {"message": "API Key is valid"}


def download_image(url: str, save_path: str):
    """URL에서 이미지 다운로드 후 저장"""
    try:
        response = requests.get(url)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("이미지 저장 완료")
    except requests.exceptions.RequestException as e:
        print(f"실패 : {e}")


def prevent_new_session(db: Session, project_id: int):
    """
    동일 프로젝트에서 'New Chat!' 세션이 존재하면 새로운 세션 생성 방지
    (첫 대화 없는 경우만 허용)
    """
    existing_sessions = db.query(ConversationSession).filter(
        ConversationSession.project_id == project_id,
        ConversationSession.session_title == 'New Chat!'
    ).first()
    if not existing_sessions:
        return None
    if is_this_first(db=db, session_id=existing_sessions.id):
        return existing_sessions
    return None


def is_not_existing(db: Session, session_id : str):
    existing = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    if not existing:
        return True
    else:
        return False