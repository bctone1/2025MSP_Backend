from pydantic import BaseModel
from typing import Optional
from typing import List

class LoginRequest(BaseModel):
    email : str
    password : str

class LoginResponse(BaseModel):
    message : str
    role : str
    email : str
    name : str

class GoogleLoginRequest(BaseModel):
    email : str
    name : str
    image : Optional[str] = None

class GoogleLoginResponse(BaseModel):
    message : str
    email : str
    name : str
    image : Optional[str] = None

class RegisterRequest(BaseModel):
    name : str
    email : str
    password : str

class RegisterResponse(BaseModel):
    message : str

class SendEmailRequest(BaseModel):
    email : str
    secretCode : str

class SendEmailResponse(BaseModel):
    message : str

class Members(BaseModel):
    name : str
    email : str
    role : str
    group : str

class GetMembersResponse(BaseModel):
    members: List[Members]
