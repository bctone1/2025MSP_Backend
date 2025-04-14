from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from database.session import get_db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from schemas.user import *
from crud.user import *

user_router = APIRouter()
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

@user_router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    name = request.name
    try:
        user_register(db, email = email, pw = password, name = name)
        return {"message": "Register Success"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@user_router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest, db : Session = Depends(get_db)):
    email = request.email
    password = request.password
    user_data = user_login(db, email, password)
    if not user_data:
        return JSONResponse(content={'message': '회원 정보가 없습니다.'}, status_code=404)
    if user_data["role"] == "admin":
        return JSONResponse(
            content={
                "message": "관리자님 반갑습니다.",
                "id": user_data["id"],
                "role": "admin",
                "email": user_data["email"],
                "name": user_data["name"]
            },
            status_code=200
        )
    elif user_data["role"] == "user":
        return JSONResponse(
            content={
                "message": f"{user_data['name']}님 반갑습니다.",
                "id": user_data["id"],
                "role": "user",
                "email": user_data["email"],
                "name": user_data["name"]
            },
            status_code=200
        )
    else:
        return JSONResponse(content={'message': '역할 정보가 없습니다.'}, status_code=400)


@user_router.post("/sendEmail", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    email = request.email
    secret_code = request.secretCode
    if not secret_code or not email:
        return JSONResponse(content={'message': 'Missing secretCode or email'}, status_code=400)
    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {secret_code}입니다."
    msg = MIMEMultipart()
    msg['From'] = config.SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={'message': '요청되었습니다'}, status_code=200)
    except Exception:
        return JSONResponse(content={'message': '이메일 전송 실패'}, status_code=500)


@user_router.post('/googlelogin', response_model=GoogleLoginResponse)
async def login(request: GoogleLoginRequest, db : Session = Depends(get_db)):
    email = request.email
    name = request.name

    try:
        user = get_user_data(db, email)

        if not user:
            user = create_google_user(db, email, name)
            return JSONResponse(
                content={
                    "message": f"{user.name}님 반갑습니다! 새 계정이 생성되었습니다.",
                    "role": user.role,
                    "email": user.email,
                    "id":user.id
                },
                status_code=200
            )
        else:
            message = "관리자님 반갑습니다." if user.role == "admin" else f"{user.name}님 반갑습니다."
            return JSONResponse(
                content={
                    "message": message,
                    "role": user.role,
                    "email": user.email,
                    "name": user.name,
                    "id" : user.id
                },
                status_code=200
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {e}")

@user_router.post("/getmembers", response_model=GetMembersResponse)
async def projects_list(db: Session = Depends(get_db)):
    member_list = get_member(db)
    return member_list

@user_router.post("/AddNewUser", response_model=AddUserResponse)
async def projects_list(request: AddUserRequest, db: Session = Depends(get_db)):
    email = request.email
    name = request.name
    role = request.role
    group = request.group
    try :
        register_by_admin(db = db, email = email, name = name, role = role, group = group)
        return JSONResponse(content={'message': '사용자가 추가 되었습니다.'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@user_router.post("/DeleteUser", response_model=DeleteUserResponse)
async def projects_list(request: DeleteUserRequest, db: Session = Depends(get_db)):
    email = request.email
    delete_user(db, email)
    return JSONResponse(content={'message': '삭제 완료.'}, status_code=200)

@user_router.post("/ChangeUserInfo", response_model=ChangeMemberResponse)
async def change_user_info_endpoint(request: ChangeMemberRequest, db: Session = Depends(get_db)):
    name = request.name
    email = request.email
    role = request.role
    group = request.group
    change_user_info(db = db, name = name, email = email, role = role, group = group)
    return JSONResponse(content={'message': '변경 완료.'}, status_code=200)

@user_router.post("/getUserInfo", response_model=GetUserInfoResponse)
async def get_user_info_endpoint(request: GetUserInfoRequest, db: Session = Depends(get_db)):
    email = request.email
    response = get_user_info(db = db, email = email)
    return response

@user_router.post("/ChangePassword", response_model=ChangePasswordResponse)
async def change_password_endpoint(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    user_id = request.ProfileData.id
    current_pw = request.newPasswordData.password
    new_pw = request.newPasswordData.newpassword
    messages = change_password(db = db, id = user_id, current_pw = current_pw, new_pw = new_pw)
    return JSONResponse(content={'message': messages}, status_code=200)

@user_router.post("/FindPassword", response_model=FindPasswordResponse)
async def find_password_endpoint(request: FindPasswordRequest, db: Session = Depends(get_db)):
    email = request.email
    new_pw = request.newPasswordData
    messages = find_password(db = db, email=email, new_pw=new_pw)
    return JSONResponse(content={'message': messages}, status_code=200)


@user_router.post("/ChangeProfile", response_model=ChangeProfileResponse)
async def change_profile_endpoint(request: ChangeProfileRequest, db: Session = Depends(get_db)):
    user_id = request.ProfileData.id
    name = request.newProfileData.name
    group = request.newProfileData.group
    change_profile(db = db, id = user_id, name = name, group = group)
    return JSONResponse(content={'message': '프로필 변경 완료.'}, status_code=200)

