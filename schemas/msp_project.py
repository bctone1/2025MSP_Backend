from pydantic import BaseModel
from typing import List, Optional

class KnowledgeSchema(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    size: Optional[str] = None
    uploaded: Optional[str] = None

    class Config:
        from_attributes = True
        # orm_mode = True #업데이트로인해 권장하지 않는 방식

class ChatSessionSchema(BaseModel):
    id: int
    title: str
    status: Optional[str] = None
    date: Optional[str] = None
    preview: Optional[str] = None
    messages: int = 0  # 메시지 개수

    class Config:
        from_attributes = True
        # orm_mode = True #업데이트로인해 권장하지 않는 방식

class ProjectSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    cost: Optional[str] = None
    conversations: List[ChatSessionSchema] = []
    knowledge: List[KnowledgeSchema] = []

    class Config:
        from_attributes = True
        # orm_mode = True #업데이트로인해 권장하지 않는 방식

class UserProjectsResponse(BaseModel):
    user_id: int
    projects: List[ProjectSchema]


class InvokeRequest(BaseModel):
    question: str
    file_paths: List[str] = []
    session_id: Optional[str] = None
    provider: str = "openai"
    model: str = "gpt-4o-mini"
