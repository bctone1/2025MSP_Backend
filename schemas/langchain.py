from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime

class FileUploadRequest(BaseModel):
    project_id: int
    user_email: str
    session_id : str
    files: List[str]

class FileUploadResponse(BaseModel):
    message: str

class RequestMessageRequest(BaseModel):
    messageInput: str
    project_id: int
    user_email: str
    session : str
    selected_model : str

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


class DeleteModelRequest(BaseModel):
    id : int
    provider_name : str
    name : str
    settings : ModelSettings

class DeleteModelResponse(BaseModel):
    message : str

class DeleteProviderRequest(BaseModel):
    id : int
    name : str
    status : str
    website : str
    description : str

class DeleteProviderResponse(BaseModel):
    message : str

class AddNewProviderRequest(BaseModel):
    name : str
    status : str
    website : str
    description : str

class AddNewProviderResponse(BaseModel):
    message : str

class AddModelSetting(BaseModel):
    temperature : float
    maxTokens : int
    topP : int
    frequencyPenalty : int
    presencePenalty : int

class AddModelRequest(BaseModel):
    provider_name : str
    name : str
    settings : AddModelSetting
    parameter : str

class AddModelResponse(BaseModel):
    message : str

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

class GetConversationRequest(BaseModel):
    email : str

class Conversation(BaseModel):
    id : int
    session_id : str
    project_id : int
    user_email : str
    message_role : str
    conversation : str
    #vector_memory : conlist(float, min_length=1536, max_length=1536)
    request_at : datetime

class GetConversationResponse(BaseModel):
    response: List[Conversation]

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
