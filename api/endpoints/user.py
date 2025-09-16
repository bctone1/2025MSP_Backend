# from fastapi import Depends, APIRouter, Request
# from fastapi.responses import JSONResponse
# from database.session import get_db
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import smtplib
# from schemas.user import *
# from crud.user import *
# from crud.llm import verify_api_key
# import json
#
#
# user_router = APIRouter(prefix="/user", tags=["user"])
#
# # SMTP 환경변수 (이메일 전송용)
# SMTP_SERVER = config.SMTP_SERVER
# SMTP_PORT = config.SMTP_PORT
# SENDER_EMAIL = config.SENDER_EMAIL
# SENDER_PASSWORD = config.SENDER_PASSWORD
#
#
# # =======================================
# # Debug: Raw JSON 확인용
# # =======================================
# @user_router.post("/Debug")
# async def test_endpoint(request: Request):
#     body = await request.json()
#     print("Raw JSON Body:", json.dumps(body, indent=2))
#     return {"message": "Got raw request"}
#
#
# # =======================================
# # 회원 가입
# # - Request: RegisterRequest
# # - Response: RegisterResponse
# # =======================================
# @user_router.post('/register', response_model=RegisterResponse)
# async def register(request: RegisterRequest, db: Session = Depends(get_db)):
#     try:
#         user_id = user_register(db, email=request.email, pw=request.password, name=request.name, phone_number=request.phone)
#         add_default_apikey(db=db, user_id=user_id)
#         return {"message": "Register Success"}
#     except Exception as e:
#         return JSONResponse(content={"message": str(e)}, status_code=500)
#
#
# # =======================================
# # 로그인
# # - Request: LoginRequest
# # - Response: LoginResponse
# # =======================================
# @user_router.post('/login', response_model=LoginResponse)
# async def login(request: LoginRequest, db: Session = Depends(get_db)):
#     user_data = user_login(db, request.email, request.password)
#     if not user_data:
#         return JSONResponse(content={'message': '회원 정보가 없습니다.'}, status_code=404)
#     if user_data["role"] == "admin":
#         return JSONResponse(content={**user_data, "message": "관리자님 반갑습니다."}, status_code=200)
#     elif user_data["role"] == "user":
#         return JSONResponse(content={**user_data, "message": f"{user_data['name']}님 반갑습니다."}, status_code=200)
#     return JSONResponse(content={'message': '역할 정보가 없습니다.'}, status_code=400)
#
#
# # =======================================
# # 이메일 인증 코드 전송
# # - Request: SendEmailRequest
# # - Response: SendEmailResponse
# # =======================================
# @user_router.post("/sendEmail", response_model=SendEmailResponse)
# async def send_email(request: SendEmailRequest):
#     if not request.secretCode or not request.email:
#         return JSONResponse(content={'message': 'Missing secretCode or email'}, status_code=400)
#
#     subject = "이메일 인증 코드"
#     body = f"귀하의 인증 코드는 {request.secretCode}입니다."
#     msg = MIMEMultipart()
#     msg['From'], msg['To'], msg['Subject'] = config.SENDER_EMAIL, request.email, subject
#     msg.attach(MIMEText(body, 'plain'))
#
#     try:
#         server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
#         server.starttls()
#         server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
#         server.sendmail(config.SENDER_EMAIL, request.email, msg.as_string())
#         server.quit()
#         return JSONResponse(content={'message': '요청되었습니다'}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={'message': f'이메일 전송 실패 : {str(e)}'}, status_code=500)
#
#
# # =======================================
# # 구글 로그인
# # - Request: GoogleLoginRequest
# # - Response: GoogleLoginResponse
# # =======================================
# @user_router.post('/googlelogin', response_model=GoogleLoginResponse)
# async def login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
#     try:
#         user_info = get_user_data(db, request.email)
#         if not user_info:
#             user = create_google_user(db, request.email, request.name)
#             add_default_apikey(db=db, user_id=user.id)
#             return JSONResponse(content={
#                 "message": f"{user.name}님 반갑습니다! 새 계정이 생성되었습니다.",
#                 "role": user.role, "email": user.email, "name": user.name, "id": user.id, "image": request.image
#             }, status_code=200)
#         else:
#             msg = "관리자님 반갑습니다." if user_info.role == "admin" else f"{user_info.name}님 반갑습니다."
#             return JSONResponse(content={
#                 "message": msg,
#                 "role": user_info.role, "email": user_info.email, "name": user_info.name,
#                 "id": user_info.id, "image": request.image
#             }, status_code=200)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"서버 오류: {e}")
#
#
# # =======================================
# # 멤버 관리 (조회/추가/삭제/변경)
# # =======================================
# @user_router.post("/getmembers", response_model=GetMembersResponse)
# async def projects_list(db: Session = Depends(get_db)):
#     return get_member(db)
#
# @user_router.post("/AddNewUser", response_model=AddUserResponse)
# async def add_user(request: AddUserRequest, db: Session = Depends(get_db)):
#     try:
#         user_id = register_by_admin(db=db, email=request.email, name=request.name, role=request.role, group=request.group)
#         add_default_apikey(db=db, user_id=user_id)
#         return JSONResponse(content={'message': '사용자가 추가 되었습니다.'}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)
#
# @user_router.post("/DeleteUser", response_model=DeleteUserResponse)
# async def delete_user_endpoint(request: DeleteUserRequest, db: Session = Depends(get_db)):
#     delete_user(db, request.email)
#     return JSONResponse(content={'message': '삭제 완료.'}, status_code=200)
#
# @user_router.post("/ChangeUserInfo", response_model=ChangeMemberResponse)
# async def change_user_info_endpoint(request: ChangeMemberRequest, db: Session = Depends(get_db)):
#     change_user_info(db=db, name=request.name, email=request.email, role=request.role,
#                      group=request.group, phone_number=request.phone_number)
#     return JSONResponse(content={'message': '변경 완료.'}, status_code=200)
#
#
# # =======================================
# # 유저 정보 조회
# # =======================================
# @user_router.post("/getUserInfo", response_model=GetUserInfoResponse)
# async def get_user_info_endpoint(request: GetUserInfoRequest, db: Session = Depends(get_db)):
#     return get_user_info(db=db, email=request.email)
#
#
# # =======================================
# # 비밀번호 변경/찾기
# # =======================================
# @user_router.post("/ChangePassword", response_model=ChangePasswordResponse)
# async def change_password_endpoint(request: ChangePasswordRequest, db: Session = Depends(get_db)):
#     msg = change_password(db=db, user_id=request.ProfileData.id,
#                           current_pw=request.newPasswordData.password,
#                           new_pw=request.newPasswordData.newpassword)
#     return JSONResponse(content={'message': msg}, status_code=200)
#
# @user_router.post("/FindPassword", response_model=FindPasswordResponse)
# async def find_password_endpoint(request: FindPasswordRequest, db: Session = Depends(get_db)):
#     msg = find_password(db=db, email=request.email, new_pw=request.newPasswordData)
#     return JSONResponse(content={'message': msg}, status_code=200)
#
#
# # =======================================
# # 프로필 변경
# # =======================================
# @user_router.post("/ChangeProfile", response_model=ChangeProfileResponse)
# async def change_profile_endpoint(request: ChangeProfileRequest, db: Session = Depends(get_db)):
#     change_profile(db=db, user_id=request.ProfileData.id,
#                    name=request.newProfileData.name,
#                    group=request.newProfileData.group,
#                    phone_number=request.newProfileData.phone_number)
#     return JSONResponse(content={'message': '프로필 변경 완료.'}, status_code=200)
#
#
# # =======================================
# # API Key 관리 (추가/삭제/변경)
# # =======================================
# @user_router.post("/AddNewAPIkey", response_model=AddNewAPIkeyResponse)
# async def add_new_apikey(request: AddNewAPIkeyRequest, db: Session = Depends(get_db)):
#     try:
#         await verify_api_key(provider=request.provider_name, api_key=request.api_key)
#     except Exception as e:
#         print(f"error occured : {e}")
#         return JSONResponse(content={"message": f"{request.api_key}"}, status_code=500)
#
#     try:
#         add_apikey(db=db, api_key=request.api_key, provider_id=request.provider_id, provider_name=request.provider_name,
#                    usage_limit=request.usage_limit, usage_count=request.usage_count, user_id=request.user.user_id)
#         return JSONResponse(content={'message': 'API 키가 정상적으로 추가되었습니다.'}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={"message": f"오류 발생 : {str(e)}"}, status_code=500)
#
# @user_router.post("/DeleteAPIKey", response_model=DeleteKeyResponse)
# async def delete_apikey_endpoint(request: DeleteKeyRequest, db: Session = Depends(get_db)):
#     try:
#         delete_apikey(db=db, key_id=request.id)
#         return JSONResponse(content={'message': 'API 키가 삭제되었습니다.'}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={'message': f'에러 발생 : {e}'}, status_code=500)
#
# @user_router.post("/ChangeAPIKey", response_model=ChangeKeyResponse)
# async def change_key_endpoint(request: ChangeKeyrequest, db: Session = Depends(get_db)):
#     try:
#         change_apikey(db=db, key_id=request.new_key.id, api_key=request.new_key.api_key)
#         return JSONResponse(content={'message': 'API 키가 변경되었습니다..'}, status_code=200)
#     except Exception as e:
#         return JSONResponse(content={'message': f'에러 발생 : {e}'}, status_code=500)
#
#
# # =======================================
# # 전화번호 인증
# # =======================================
# @user_router.post("/Phonerequest", response_model=PhoneResponse)
# async def phone_request_endpoint(request: PhoneRequest, db: Session = Depends(get_db)):
#     result = sms_verfication(db=db, phone_number=request.phone_number, phoneCode=request.phoneCode)
#     return JSONResponse(content={'message': f'{result}'}, status_code=200)
#
#
# # =======================================
# # 이메일 찾기
# # =======================================
# @user_router.post("/findemail", response_model=FindEmailResponse)
# async def find_email_endpoint(request: FindEmailRequest, db: Session = Depends(get_db)):
#     result = findemail_method(db=db, phone=request.phone, name=request.name, secretCode=request.secretCode)
#     if result:
#         return JSONResponse(content={'email': f'{result}', 'message': '성공'}, status_code=200)
#     return JSONResponse(content={'email': '가입된 이메일이 없습니다.', 'message': '실패'}, status_code=200)
