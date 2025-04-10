from pydantic import BaseModel
from typing import Optional
from typing import List

class LoginRequest(BaseModel):
    email : str
    password : str

class LoginResponse(BaseModel):
    message : str
    id : int
    role : str
    email : str
    name : str

class GoogleLoginRequest(BaseModel):
    email : str
    name : str
    image : Optional[str] = None

class GoogleLoginResponse(BaseModel):
    id : int
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

class AddUserRequest(BaseModel):
    name : str
    email : str
    role : str
    group : str

class AddUserResponse(BaseModel):
    message : str

class DeleteUserRequest(BaseModel):
    email: str

class DeleteUserResponse(BaseModel):
    message : str

class ChangeMemberRequest(BaseModel):
    name : str
    email : str
    role : str
    group : str

class ChangeMemberResponse(BaseModel):
    message : str

class GetUserInfoRequest(BaseModel):
    email : str


class GetUserInfoResponse(BaseModel):
    id : int
    email : str
    password : str
    name : str
    role : str
    group : str

class NewPasswordData(BaseModel):
    password : str
    newpassword : str
    confirmPassword : str

class ProfileData(BaseModel):
    id : int
    email : str
    password : str
    name : str
    role : str
    group : str

class ChangePasswordRequest(BaseModel):
    newPasswordData : NewPasswordData
    ProfileData : ProfileData

class ChangePasswordResponse(BaseModel):
    message : str

class NewProfileData(BaseModel):
    name : str
    group : str

class ChangeProfileRequest(BaseModel):
    newProfileData : NewProfileData
    ProfileData : ProfileData

class ChangeProfileResponse(BaseModel):
    message: str

class FindPasswordRequest(BaseModel):
    newPasswordData : str
    email : str

class FindPasswordResponse(BaseModel):
    message : str