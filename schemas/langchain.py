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

