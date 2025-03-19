from pydantic import BaseModel
from typing import Optional

class FileRequest(BaseModel):
    project_id : int
    file_name : str

class FileResponse(BaseModel):
    message : str

class AgentRequest(BaseModel):
    project_id: int
    query: str
    provider: Optional[str] = "openai"
    model: Optional[str] = None