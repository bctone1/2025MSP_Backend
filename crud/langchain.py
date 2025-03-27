import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from models.project import ProjectInfoBase
from models.api import ConversationLog, AIModel, Provider, ApiKey
from sqlalchemy import select
from pgvector.sqlalchemy import Vector
import numpy as np

def upload_file(db: Session, project: int, email: str, url: str, vector: list):
    try:
        # 벡터를 PGVector 형식으로 변환
        vector = np.array(vector)  # 벡터를 numpy 배열로 변환
        vector = vector.flatten()  # 벡터를 1차원 배열로 변환
        print(f"Uploading vector of length {len(vector)}")

        # 새로운 파일을 추가
        new_file = ProjectInfoBase(
            project_id=project,
            user_email=email,
            file_url=url,
            vector_memory=vector,  # 벡터 값을 vector_memory 컬럼에 저장
            upload_at=datetime.utcnow()  # 업로드 시간 설정
        )

        # 데이터베이스에 추가 및 커밋
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        # 결과 반환
        print(f"Uploaded file with vector: {new_file.vector_memory}")
        return new_file

    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        print(f"Error occurred: {str(e)}")
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
    """세션 ID 기준으로 대화 기록을 DB에서 가져오기"""
    stmt = select(ConversationLog).where(ConversationLog.session_id == session_id).order_by(ConversationLog.request_at)
    results = db.execute(stmt).scalars().all()

    history_messages = []
    for msg in results:
        history_messages.append({
            'message_role': msg.message_role,
            'conversation': msg.conversation
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