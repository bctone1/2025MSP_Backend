import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from models.project import ProjectInfoBase, InfoList, User
from models.api import ConversationLog, AIModel, Provider, ApiKey, ConversationSession
from sqlalchemy import select
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import numpy as np

def upload_file(db: Session, project: int, email: str, url: str):
    try:
        # 벡터를 PGVector 형식으로 변환
        #vector = np.array(vector)  # 벡터를 numpy 배열로 변환
        #vector = vector.flatten()  # 벡터를 1차원 배열로 변환
        #print(f"Uploading vector of length {len(vector)}")

        # 새로운 파일을 추가
        new_file = ProjectInfoBase(
            project_id=project,
            user_email=email,
            file_url=url,
            upload_at=datetime.utcnow()  # 업로드 시간 설정
        )
        # 데이터베이스에 추가 및 커밋
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        print(f"IIIIDDDD: {new_file.id}")

        return new_file.id

    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        print(f"Error occurred: {str(e)}")
        raise e

def save_info(db: Session, infobase_id : int, content : str, vector_memory : list):
    try:
        new_info = InfoList(
            infobase_id = infobase_id,
            content = content,
            vector_memory = vector_memory,
            upload_at=datetime.utcnow()
        )
        db.add(new_info)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error occured : {str(e)}")
        raise e


def add_message(db : Session, session_id : int, project_id : int, user_email : str, message_role : str, conversation : str, vector_memory : list):
    try:
        vector = np.array(vector_memory)  # 벡터를 numpy 배열로 변환
        vector = vector.flatten()  # 벡터를 1차원 배열로 변환

        new_message = ConversationLog(
            session_id = session_id,
            project_id = project_id,
            user_email = user_email,
            message_role = message_role,
            conversation = conversation,
            vector_memory = vector,
            request_at = datetime.utcnow()
        )
        db.add(new_message)
        db.commit()
        return {"message": "Message saved successfully!", "request_at": new_message.request_at}
    except Exception as e:
        db.rollback()
        print(f"Error occured : {str(e)}")
        raise e



def get_chat_history(db: Session, session_id: int):
    """세션 ID 기준으로 대화 기록과 추가 정보를 DB에서 가져오기"""
    history_messages = []

    # 1. conversation_logs 테이블 조회
    stmt = select(ConversationLog).where(ConversationLog.session_id == session_id).order_by(ConversationLog.request_at)
    results = db.execute(stmt).scalars().all()

    # ✅ 결과가 없으면 바로 빈 리스트 반환
    if not results:
        return history_messages

    # 2. 첫 번째 결과에서 project_id 가져오기
    project_id = results[0].project_id

    # 3. project_id를 이용해 info_base 조회
    info_base_stmt = select(ProjectInfoBase).where(ProjectInfoBase.project_id == project_id)
    info_base_result = db.execute(info_base_stmt).scalar()  # ✅ 첫 번째 결과 가져오기
    print(f"😊results : {project_id}😊")
    if info_base_result:
        info_id = info_base_result.id

        # 4. info_list 조회
        info_list_stmt = select(InfoList).where(InfoList.infobase_id == info_id).order_by(InfoList.upload_at)
        infos = db.execute(info_list_stmt).scalars().all()

        # 5. info_list 내용을 history_messages에 추가
        for info in infos:
            history_messages.append({
                'message_role': "System",
                'conversation': info.content,
                'vector_memory': info.vector_memory
            })

    # 6. 기존 conversation_logs 내용도 history_messages에 추가
    for msg in results:
        history_messages.append({
            'message_role': msg.message_role,
            'conversation': msg.conversation,
            'vector_memory': msg.vector_memory
        })
    print(f"😊😊😊😊😊😊😊😊😊😊history message : {history_messages}😊😊😊😊😊😊😊😊😊😊")
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

def get_api_keys(db: Session):
    keys = db.execute(select(ApiKey)).scalars().all()
    return {
        "api_keys": [
            {
                "id" : k.id,
                "provider_id" : k.provider_id,
                "provider_name" : k.provider_name,
                "user_id" : k.user_id,
                "api_key" : k.api_key,
                "status" : k.status,
                "create_at" : k.create_at,
                "usage_limit" : k.usage_limit,
                "usage_count" : k.usage_count
            } for k in keys
        ]
    }
'''
def get_session(db: Session, email : str):
    session = db.query(ConversationSession).filter(ConversationSession.user_email == email).all()
    if session :
        return {
            "response": [
                {
                    "id": s.id,
                    "session_title": s.session_title,
                    "project_id": s.project_id,
                    "user_email": s.user_email,
                    "register_at" : s.register_at
                } for s in session
            ]
        }
'''


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
    session = db.query(ConversationLog).filter(ConversationLog.user_email == email).all()
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
                    #"vector_memory" : s.vector_memory,
                    "request_at" : s.request_at
                } for s in session
            ]
        }
def add_new_session(db: Session, id : str, project_id : int, session_title : str, user_email : str):
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

def is_this_first(db: Session, id : str):
    first_conversation = db.query(ConversationLog).filter_by(session_id=id).order_by(ConversationLog.request_at.asc()).first()
    if first_conversation is None :
        print("THIS IS FIRST ")
        return True

def change_session_title(db : Session, session_id : str, content : str):
    session = db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
    session.session_title = content
    db.commit()
    db.refresh(session)
    return session

def get_embedding_key(db : Session):
    api = db.query(ApiKey).filter(ApiKey.user_id == 1).first()
    config.EMBEDDING_API = api.api_key
    return config.EMBEDDING_API

def get_api_key(db : Session, user_email : str, provider = str):
    user = db.query(User).filter(User.email == user_email).first()
    user_id = user.id
    if provider == 'openai':
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id==4).first()
        config.GPT_API = api.api_key
        get_embedding_key(db=db)
    elif provider == "anthropic":
        api = db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.provider_id==2).first()
        config.CLAUDE_API = api.api_key
        get_embedding_key(db=db)
    if provider:
        return api.api_key

