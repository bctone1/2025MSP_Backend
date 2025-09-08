from fastapi import APIRouter, Request, UploadFile, File, Form, Depends

from database.session import get_db #DB 커넥션
from crud.msp_user import create_user, get_user_by_email, create_social_user  # CRUD 임포트
from crud.user import *

user_router = APIRouter(tags=["msp_user"], prefix="/MSP_USER")




# 로그인
@user_router.post("/MSPLogin")
async def MSPLogin(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("user_email")
    password = body.get("user_pw")
    login_method = body.get("loginMethod")

    # ✅ DB 조회
    user = get_user_by_email(db, email=email)

    # ✅ 비회원
    if not user:
        return {
            "response": "회원정보가 없습니다.",
            "status": False,
        }
    # ✅ 사용자의 권한이 로그인 방법과 틀림
    if user.role != login_method:
        return{
            "response": "로그인 정보가 없습니다. 사용자 역할을 올바르게 선택하세요",
            "status": False,
        }
    # ✅ 비밀번호 검증 (bcrypt 사용 가정)
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return {
            "response": "비밀번호가 틀립니다.",
            "status": False,
        }
    # ✅ 로그인 성공
    return {
        "response": f"{'관리자' if user.role == 'admin' else '유저'} 로그인 성공",
        "status": True,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "id" : user.user_id
    }


# 소셜로그인
@user_router.post("/MSPSocialLogin")
async def MSPSocialLogin(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("email")
    name = body.get("name")
    image = body.get("image")

    if not email:
        return {"error": "이메일 필요"}

    user = create_social_user(db=db, email=email, name=name, profile_image=image)

    return {
        "response": "로그인 성공",
        "user_id": user.user_id,
        "name": user.name,
        "id":user.user_id
    }





# 이메일 중복체크 요청
@user_router.post("/MSPCheckEmail")
async def MSPCheckEmail(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    email = body.get("email")

    if not email:
        return {
            "response": "이메일을 입력해주세요.",
            "result": False
        }

    # ✅ crud 사용해서 DB 조회
    user = get_user_by_email(db, email=email)
    print(user)

    if user:
        return {
            "response": "이미 가입된 이메일 입니다!",
            "result": False
        }
    else:
        return {
            "response": "사용 가능한 이메일 입니다!",
            "result": True
        }




# 회원가입 요청
@user_router.post("/MSPRegister")
async def MSPRegister(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print(body)
    firstName = body.get("register").get("firstName")
    lastName= body.get("register").get("lastName")
    email = body.get("register").get("email")
    password = body.get("register").get("password")
    termsAgreed = body.get("register").get("termsAgreed")
    marketingAgreed = body.get("register").get("marketingAgreed")

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        new_user = create_user(
            db=db,
            email=email,
            password_hash=hashed_pw,
            name=firstName+lastName,
            role="user",
            terms_agreed = termsAgreed,
            marketing_agreed = marketingAgreed
        )
        print(f"신규 사용자 생성됨: ID={new_user.user_id}, Email={new_user.email}")

        return {
            "response": "가입이 완료되었습니다!",
            "result": True
        }
    except ValueError:
        return {
            "response": "이미 가입된 이메일입니다!",
            "result": True
        }
        # raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")