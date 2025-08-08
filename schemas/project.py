from pydantic import BaseModel
from typing import List, Optional

class ProjectInfo(BaseModel):
    project_name: str
    description: str
    category: str
    model: str
    user_email: str
    provider: str

class FileData(BaseModel):
    id: Optional[int] = None
    name: str
    source: str

class ActiveProject(BaseModel):
    project_id: int
    user_email: str
    project_name: str
    category: str
    description: str
    provider: str
    ai_model: str


class CreateProjectRequest(BaseModel):
    projectInfo: ProjectInfo

class CreateProjectResponse(BaseModel):
    message : str


class ProjectListRequest(BaseModel):
    email : str

class ProjectListResponse(BaseModel):
    project_id: int
    user_email: str
    project_name: str
    category: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    ai_model: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class Provider(BaseModel):
    id : int
    name: str
    status: str
    website: str
    description: str

class ProviderListResponse(BaseModel):
    providers : List[Provider]

class DeleteSessionRequest(BaseModel):
    session_id : str

class DeleteSessionResponse(BaseModel):
    message : str

class DeleteFileRequest(BaseModel):
    file: FileData
    activeProject: ActiveProject

class DeleteFileResponse(BaseModel):
    message :str

class DeleteProjectRequest(BaseModel):
    project_ids: List[int]

class DeleteProjectResponse(BaseModel):
    message:str


