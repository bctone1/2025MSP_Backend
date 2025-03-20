from pydantic import BaseModel

class ProjectInfo(BaseModel):
    name: str
    desc: str
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

class RequestMessageRequest(BaseModel):
    messageInput : str
    project_id : int
    user_email : str