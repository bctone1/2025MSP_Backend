from pydantic import BaseModel, Field
from typing import Optional
from typing import List

# =======================================
#  유저 기본 정보
# =======================================
class UserInfo(BaseModel):
    user_id: int = Field(..., alias="id")
    user_name: str = Field(..., alias="name")
    email: str

# =======================================
#  로그인 & 소셜 로그인
# =======================================
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
    role : str
    image : Optional[str] = None

# =======================================
#  회원 가입
# =======================================
class RegisterRequest(BaseModel):
    name : str
    email : str
    password : str
    phone: str

class RegisterResponse(BaseModel):
    message : str

# =======================================
#  이메일 인증
# =======================================
class SendEmailRequest(BaseModel):
    email : str
    secretCode : str

class SendEmailResponse(BaseModel):
    message : str

# =======================================
#  멤버 관리
# =======================================
class Members(BaseModel):
    name : str
    email : str
    role : str
    group : str
    phone_number: Optional[str] = None

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
    phone_number : str

class ChangeMemberResponse(BaseModel):
    message : str

# =======================================
#  유저 정보 조회
# =======================================
class GetUserInfoRequest(BaseModel):
    email : str

class GetUserInfoResponse(BaseModel):
    id : int
    email : str
    password : str
    name : str
    role : str
    group : str
    phone_number: Optional[str] = None

# =======================================
#  비밀번호 변경
# =======================================
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

# =======================================
#  프로필 변경
# =======================================
class NewProfileData(BaseModel):
    name : str
    group : str
    phone_number: str

class ChangeProfileRequest(BaseModel):
    newProfileData : NewProfileData
    ProfileData : ProfileData

class ChangeProfileResponse(BaseModel):
    message: str

# =======================================
#  비밀번호 찾기/재설정
# =======================================
class FindPasswordRequest(BaseModel):
    newPasswordData : str
    email : str

class FindPasswordResponse(BaseModel):
    message : str

# =======================================
#  API Key 관리
# =======================================
class AddNewAPIkeyRequest(BaseModel):
    api_key : str
    provider_id : int
    provider_name : str
    usage_limit : int
    usage_count : int
    user: UserInfo

class AddNewAPIkeyResponse(BaseModel):
    message : str

class DeleteKeyRequest(BaseModel):
    id : int

class DeleteKeyResponse(BaseModel):
    message : str

class NewKey(BaseModel):
    id: int
    api_key: str

class ChangeKeyrequest(BaseModel):
    new_key: NewKey

class ChangeKeyResponse(BaseModel):
    message : str

# =======================================
#  전화번호 인증
# =======================================
class PhoneRequest(BaseModel):
    phone_number : str
    phoneCode : str

class PhoneResponse(BaseModel):
    message : str

# =======================================
#  이메일 찾기
# =======================================
class FindEmailRequest(BaseModel):
    name : str
    phone : str
    secretCode : str

class FindEmailResponse(BaseModel):
    message : str
    email : str
