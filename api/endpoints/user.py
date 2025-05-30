from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from database.session import get_db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from schemas.user import *
from crud.user import *
from fastapi import Request
from crud.llm import verify_api_key
import json

user_router = APIRouter()
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD

@user_router.post("/Debug")
async def test_endpoint(request: Request):
    body = await request.json()
    print("Raw JSON Body:", json.dumps(body, indent=2))
    return {"message": "Got raw request"}


@user_router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    name = request.name
    phone_number = request.phone
    try:
        user_id = user_register(db, email = email, pw = password, name = name, phone_number = phone_number)
        add_default_apikey(db = db, user_id = user_id)
        return {"message": "Register Success"}
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

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
    except Exception as e:
        return JSONResponse(content={'message': f'이메일 전송 실패 : {str(e)}'}, status_code=500)


@user_router.post('/googlelogin', response_model=GoogleLoginResponse)
async def login(request: GoogleLoginRequest, db : Session = Depends(get_db)):
    email = request.email
    name = request.name
    image = request.image

    try:
        user_info = get_user_data(db, email)

        if not user_info:
            user = create_google_user(db, email, name)
            add_default_apikey(db=db, user_id=user.id)
            return JSONResponse(
                content={
                    "message": f"{user.name}님 반갑습니다! 새 계정이 생성되었습니다.",
                    "role": user.role,
                    "email": user.email,
                    "name": user.name,
                    "id" : user.id,
                    "image" : image

                },
                status_code=200
            )
        else:
            message = "관리자님 반갑습니다." if user_info.role == "admin" else f"{user_info.name}님 반갑습니다."
            return JSONResponse(
                content={
                    "message": message,
                    "role": user_info.role,
                    "email": user_info.email,
                    "name": user_info.name,
                    "id" : user_info.id,
                    "image": image
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
        user_id = register_by_admin(db = db, email = email, name = name, role = role, group = group)
        add_default_apikey(db=db, user_id=user_id)
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
    phone_number = request.phone_number

    change_user_info(db = db, name = name, email = email, role = role, group = group, phone_number = phone_number)
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
    messages = change_password(db = db, user_id = user_id, current_pw = current_pw, new_pw = new_pw)
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
    phone_number = request.newProfileData.phone_number

    change_profile(db = db, user_id = user_id, name = name, group = group, phone_number = phone_number)
    return JSONResponse(content={'message': '프로필 변경 완료.'}, status_code=200)


@user_router.post("/AddNewAPIkey", response_model = AddNewAPIkeyResponse)
async def add_new_apikey(request: AddNewAPIkeyRequest, db : Session = Depends(get_db)):
    api_key = request.api_key
    provider_id = request.provider_id
    provider_name = request.provider_name
    usage_limit = request.usage_limit
    usage_count = request.usage_count
    user_id = request.user.user_id
    try:
        await verify_api_key(provider=provider_name, api_key=api_key)
    except Exception as e:
        print(f"error occured : {e}")
        return JSONResponse(content={"message": f"{api_key}"}, status_code=500)
    try :
        add_apikey(db=db, api_key=api_key, provider_id=provider_id, provider_name=provider_name,
                   usage_limit=usage_limit, usage_count=usage_count, user_id=user_id)
        return JSONResponse(content={'message': 'API 키가 정상적으로 추가되었습니다.'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"오류 발생 : {str(e)}"}, status_code=500)

@user_router.post("/Phonerequest", response_model=PhoneResponse)
async def find_email_endpoint(request: PhoneRequest, db: Session = Depends(get_db)):
    phone_number = request.phone_number
    phone_code = request.phoneCode

    result = sms_verfication(db = db, phone_number = phone_number, phoneCode = phone_code)
    return JSONResponse(content={'message' : f'{result}'}, status_code=200)

@user_router.post("/findemail", response_model=FindEmailResponse)
async def find_email_endpoint(request: FindEmailRequest, db: Session = Depends(get_db)):
    phone = request.phone
    name = request.name
    secret_code = request.secretCode

    result =findemail_method(db =db, phone=phone, name = name, secretCode=secret_code)

    if result :
        return JSONResponse(content={'email' : f'{result}', 'message' : '성공'}, status_code=200)
    else :
        return JSONResponse(content={'email' : '가입된 이메일이 없습니다.', 'message' : '실패'}, status_code=200)

@user_router.post("/DeleteAPIKey", response_model=DeleteKeyResponse)
async def delete_apikey_endpoint(request: DeleteKeyRequest, db: Session = Depends(get_db)):
    key_id = request.id
    try :
        delete_apikey(db = db, key_id = key_id)
        return JSONResponse(content={'message': 'API 키가 삭제되었습니다.'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'message' : f'에러 발생 : {e}'}, status_code=500)

@user_router.post("/ChangeAPIKey", response_model=ChangeKeyResponse)
async def change_key_endpoint(request: ChangeKeyrequest, db: Session = Depends(get_db)):
    api_key = request.new_key.api_key
    key_id = request.new_key.id
    try :
        change_apikey(db = db, key_id = key_id, api_key=api_key)
        return JSONResponse(content={'message': 'API 키가 변경되었습니다..'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'message' : f'에러 발생 : {e}'}, status_code=500)