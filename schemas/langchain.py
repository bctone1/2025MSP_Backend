from pydantic import BaseModel
from typing import List


class FileUploadRequest(BaseModel):
    project_id: str
    user_email: str
    files: List[str]

class FileUploadResponse(BaseModel):
    message: str
    files: List[str]

class RequestMessageRequest(BaseModel):
    messageInput: str
    project_id: int
    user_email: str

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

