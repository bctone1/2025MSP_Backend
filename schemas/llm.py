from __future__ import annotations

from pydantic import BaseModel
from typing import List
from datetime import datetime

# =======================================
#  테스트 요청
# =======================================
class TestRequest(BaseModel):
    message: str
    user_email : str

# =======================================
# 💬 LLM 메시지 요청
# =======================================
class RequestMessageRequest(BaseModel):
    messageInput: str
    project_id: int
    user_email: str
    session : str
    selected_model : str

# =======================================
#  모델 목록 및 설정
# =======================================
class ModelList(BaseModel):
    id : int
    model_name : str
    provider_id : int
    provider_name : str

class ModelListResponse(BaseModel):
    models: List[ModelList]

class ModelSettings(BaseModel):
    temperature : float
    maxTokens : int
    topP : int
    frequencyPenalty : int
    presencePenalty : int
    isDefault : bool

# =======================================
# ️ 모델 삭제
# =======================================
class DeleteModelRequest(BaseModel):
    id : int
    provider_name : str
    name : str
    # settings : ModelSettings

class DeleteModelResponse(BaseModel):
    message : str

# =======================================
# ️ 제공자 삭제
# =======================================
class DeleteProviderRequest(BaseModel):
    id : int
    name : str
    status : str
    website : str
    description : str

class DeleteProviderResponse(BaseModel):
    message : str

# =======================================
#  제공자 추가
# =======================================
class AddNewProviderRequest(BaseModel):
    name : str
    status : str
    website : str
    description : str

class AddNewProviderResponse(BaseModel):
    message : str

# =======================================
#  모델 추가
# =======================================
class AddModelSetting(BaseModel):
    temperature : float
    maxTokens : int
    topP : int
    frequencyPenalty : int
    presencePenalty : int

class AddModelRequest(BaseModel):
    provider_name : str
    name : str
    # settings : AddModelSetting
    # parameter : str

class AddModelResponse(BaseModel):
    message : str

# =======================================
#  모델 변경
# =======================================
class ChangeModelBefore(BaseModel):
    id : int
    provider_name : str
    name : str
    settings : ModelSettings

class ChangeModelNew(BaseModel):
    id : int
    provider_name : str
    name : str
    settings : ModelSettings

class ChangeModelRequest(BaseModel):
    model_before : ChangeModelBefore
    model_new : ChangeModelNew

class ChangeModelResponse(BaseModel):
    message : str

# =======================================
#  세션 조회
# =======================================
class GetSessionRequest(BaseModel):
    email : str

class Session(BaseModel):
    id : str
    session_title : str
    project_id : int
    user_email : str
    register_at: datetime

class GetSessionResponse(BaseModel):
    response: List[Session]

# =======================================
#  대화 조회
# =======================================
class GetConversationRequest(BaseModel):
    email : str

class Conversation(BaseModel):
    id : int
    session_id : str
    project_id : int
    user_email : str
    message_role : str
    conversation : str
    request_at : datetime
    case : str

class GetConversationResponse(BaseModel):
    response: List[Conversation]

# =======================================
#  새 세션 생성
# =======================================
class NewSessionRequest(BaseModel):
    id : str
    project_id : int
    session_title : str
    register_at : str
    messages: int
    user_email : str

class NewSessionResponse(BaseModel):
    id : str
    project_id : int
    session_title : str
    register_at : datetime
    user_email : str

# =======================================
#  활성 프로젝트 정보
# =======================================
class ActiveProject(BaseModel):
    project_id: int
    user_email: str
    project_name: str
    category: str
    description: str
    provider: str
    ai_model: str

class GetInfoBaseRequest(BaseModel):
    activeProject: ActiveProject

# =======================================
#  제공자 상태 확인
# =======================================
class ProviderStatusRequest(BaseModel):
    provider_id : int

class ProviderStatusResponse(BaseModel):
    message : str
