from pydantic import BaseModel, Field
from typing import Optional
from typing import List

class UserInfo(BaseModel):
    user_id: int = Field(..., alias="id")
    user_name: str = Field(..., alias="name")
    email: str

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
    phone_number: str

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

class AddNewAPIkeyRequest(BaseModel):
    api_key : str
    provider_id : int
    provider_name : str
    usage_limit : int
    usage_count : int
    user: UserInfo

class AddNewAPIkeyResponse(BaseModel):
    message : str

class PhoneRequest(BaseModel):
    phone_number : str
    phoneCode : str

class PhoneResponse(BaseModel):
    message : str

class FindEmailRequest(BaseModel):
    name : str
    phone : str
    secretCode : str

class FindEmailResponse(BaseModel):
    message : str
    email : str