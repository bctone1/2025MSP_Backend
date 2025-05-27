import core.config as config
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from models.user import User
from models.project import ProjectInfoBase, InfoList
from models.llm import ConversationLog, AIModel, Provider, ApiKey, ConversationSession
from sqlalchemy import select
from sqlalchemy.sql import func
from langchain_service.llms.setup import get_llm
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from core.tools import mask_api_key
import os
import requests
def upload_file(db: Session, project: int, email: str, url: str, name : str):
    try:
        new_file = ProjectInfoBase(
            project_id=project,
            user_email=email,
            file_url=url,
            upload_at = datetime.now(UTC),
            file_name = name
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file.id

    except Exception as e:
        db.rollback()
        raise e

def save_info(db: Session, infobase_id : int, content : str, vector_memory : list):
    try:
        new_info = InfoList(
            infobase_id = infobase_id,
            content = content,
            vector_memory = vector_memory,
            upload_at = datetime.now(UTC)
        )
        db.add(new_info)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def add_message(db : Session, session_id : str, project_id : int, user_email : str, message_role : str, conversation : str, vector_memory : list):
    try:
        vector = np.array(vector_memory)
        vector = vector.flatten()

        new_message = ConversationLog(
            session_id = session_id,
            project_id = project_id,
            user_email = user_email,
            message_role = message_role,
            conversation = conversation,
            vector_memory = vector,
            request_at = datetime.now(UTC)
        )
        db.add(new_message)
        db.commit()
        return {"message": "Message saved successfully!", "request_at": new_message.request_at}
    except Exception as e:
        db.rollback()
        raise e

def get_chat_history(db: Session, session_id: int):
    history_messages = []
    stmt = select(ConversationLog).where(ConversationLog.session_id == session_id).order_by(ConversationLog.request_at)
    results = db.execute(stmt).scalars().all()
    if not results:
        return history_messages

    project_id = results[0].project_id

    info_base_stmt = select(ProjectInfoBase).where(ProjectInfoBase.project_id == project_id)
    info_base_result = db.execute(info_base_stmt).scalar()
    if info_base_result:
        info_id = info_base_result.id

        info_list_stmt = select(InfoList).where(InfoList.infobase_id == info_id).order_by(InfoList.upload_at)
        infos = db.execute(info_list_stmt).scalars().all()

        for info in infos:
            history_messages.append({
                'message_role': "System",
                'conversation': info.content,
                'vector_memory': info.vector_memory
            })

    for msg in results:
        history_messages.append({
            'message_role': msg.message_role,
            'conversation': msg.conversation,
            'vector_memory': msg.vector_memory
        })
    return history_messages


def get_model_list(db: Session):
    models = db.execute(select(AIModel.id, AIModel.model_name, AIModel.provider_id, AIModel.provider_name)).all()
    return {
        "models" : [
            {
                "id": m.id,
                "model_name": m.model_name,
                "provider_id": m.provider_id,
                "provider_name": m.provider_name,
            } for m in models
        ]
    }

def delete_model(db: Session, model_id : int):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    db.delete(model)
    db.commit()
    return "Deleted"

def delete_provider(db: Session, provider_id : int):
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

def add_provider(db: Session, name : str, status : str, website : str, description : str):
    new_provider = Provider(
        name = name,
        status = status,
        website = website,
        description = description
    )
    db.add(new_provider)
    db.commit()

def add_model(db: Session, provider_name : str, name : str):
    provider_id = db.query(Provider.id).filter(Provider.name == provider_name).scalar()
    new_model = AIModel(
        model_name = name,
        provider_id = provider_id,
        provider_name = provider_name
    )
    db.add(new_model)
    db.commit()

def change_model(db: Session, id : int, provider_name : str, name : str):
    provider_id = db.query(Provider.id).filter(Provider.name == provider_name).scalar()
    model = db.query(AIModel).filter(AIModel.id == id).first()
    if model:
        model.model_name = name,
        model.provider_id = provider_id,
        model.provider_name = provider_name

        db.commit()
        db.refresh(model)
        return model
    else:
        return None

def get_api_keys(db: Session, email: str):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return {"api_keys": [],"message":"please enter your apikey"}

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

def get_session(db: Session, email : str):
    subquery = (
        db.query(
            ConversationLog.session_id,
            func.count().label("messages")
        )
        .filter(ConversationLog.message_role == 'assistant')
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
        session_dict['messages'] = messages  # messages 값을 추가
        result.append(session_dict)
    return result

def get_conversation(db: Session, email : str):
    session = db.query(ConversationLog).filter(ConversationLog.user_email == email).order_by(ConversationLog.id).all()
    if session :
        return {
            "response": [
                {
                    "id": s.id,
                    "session_id": s.session_id,
                    "project_id": s.project_id,
                    "user_email": s.user_email,
                    "message_role" : s.message_role,
                    "conversation" : s.conversation,
                    "request_at" : s.request_at
                } for s in session
            ]
        }

def add_new_session(db: Session, id : str, project_id : int, session_title : str, user_email : str):
    already_exists = db.query(ConversationSession).filter(ConversationSession.id == id).first()
    if already_exists :
        return "already_exist"
    new_session = ConversationSession(
        id  = id,
        session_title = session_title,
        register_at = datetime.utcnow(),
        project_id = project_id,
        user_email = user_email
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def is_this_first(db: Session, session_id : str):
    first_conversation = db.query(ConversationLog).filter_by(session_id=session_id).order_by(ConversationLog.request_at.asc()).first()
    return first_conversation is None

def change_session_title(db : Session, session_id : str, content : str):
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    session.session_title = content
    db.commit()
    db.refresh(session)
    return session


def get_api_key(db: Session, user_email: str, provider: str):
    user = db.query(User).filter(User.email == user_email).first()

    user_id = user.id
    if provider == 'openai':
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id==4).first()
        if not api:
            return None
        return api.api_key
    elif provider == "anthropic":
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id==2).first()
        if not api:
            return None
        elif api.api_key == 'Default API Key':
            return config.DEFAULT_API_KEY
        return api.api_key



def get_infobase(db: Session, email: str, project_id: int):
    stmt = select(ProjectInfoBase).where(
        ProjectInfoBase.project_id == project_id,
        ProjectInfoBase.user_email == email
    )
    return db.scalars(stmt).all()

def change_provider_status(db: Session, provider_id: int):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    print(f"provider_Status : {provider.status}")
    if provider.status == 'Active':
        provider.status = 'Deactive'
    elif provider.status == 'Deactive':
        provider.status = 'Active'
    db.commit()
    db.refresh(provider)

async def verify_api_key(provider: str, api_key: str, model: str = None):
    try:
        provider = provider.lower()
        llm = get_llm(provider=provider, model=model, api_key=api_key)

        # 간단한 프롬프트
        prompt = ChatPromptTemplate.from_messages([
            ("user", "Say hello")
        ])

        chain = prompt | llm

        # 실제 요청 (최소 토큰 요청)
        response = await chain.ainvoke({})

        if not response:
            raise ValueError("Empty response received.")

    except Exception as e:
        # 예외 발생하면 키가 유효하지 않다고 판단
        raise ValueError(f"API Key 검증 실패: {str(e)}")

    return {"message": "API Key is valid"}

def download_image(url: str, save_path: str):
    try:
        response = requests.get(url)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as f :
            f.write(response.content)
        print("이미지 저장 완료")
    except requests.exceptions.RequestException as e:
        print(f"실패 : {e}")

def prevent_new_session(db: Session, project_id: int):
    existing_sessions = db.query(ConversationSession).filter(
        ConversationSession.project_id == project_id
    ).first()
    if not existing_sessions:
        return None
    if existing_sessions.session_title == "New Chat!":
        return existing_sessions
    if is_this_first(db=db, session_id=existing_sessions.id):
        return existing_sessions
    return None