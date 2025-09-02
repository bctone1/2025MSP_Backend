from pydantic import BaseModel
from typing import List, Optional

class KnowledgeSchema(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    size: Optional[str] = None
    uploaded: Optional[str] = None

    class Config:
        orm_mode = True

class ChatSessionSchema(BaseModel):
    id: int
    title: str
    status: Optional[str] = None
    date: Optional[str] = None
    preview: Optional[str] = None
    messages: int = 0  # 메시지 개수

    class Config:
        orm_mode = True

class ProjectSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    cost: Optional[str] = None
    conversations: List[ChatSessionSchema] = []
    knowledge: List[KnowledgeSchema] = []

    class Config:
        orm_mode = True

class UserProjectsResponse(BaseModel):
    user_id: int
    projects: List[ProjectSchema]
