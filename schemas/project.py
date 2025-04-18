from pydantic import BaseModel
from typing import List

class ProjectInfo(BaseModel):
    project_name: str
    description: str
    category: str
    model: str
    user_email: str
    provider: str

class CreateProjectRequest(BaseModel):
    projectInfo: ProjectInfo

class CreateProjectResponse(BaseModel):
    message : str


class ProjectListRequest(BaseModel):
    email : str

class ProjectListResponse(BaseModel):
    projects : str
    categories : str
    models : str
    selectProject : int
    setView : str


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
    infobase_id :int

class DeleteFileResponse(BaseModel):
    message :str