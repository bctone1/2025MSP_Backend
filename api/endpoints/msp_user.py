from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from core.config import GOOGLE_API, CLAUDE_API, OPENAI_API
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI
from fastapi.responses import JSONResponse
import anthropic


from database.session import get_db #DB 커넥션
from crud.msp_user import create_user, get_user_by_email, create_social_user  # CRUD 임포트

from crud.user import *
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart



# SMTP 환경변수 (이메일 전송용)
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_PASSWORD = config.SENDER_PASSWORD




test_router = APIRouter(tags=["msp_user"], prefix="/MSP_USER")

# 랭체인 구글 예시
@test_router.post("/googlerequest")
async def googlerequest(request: Request):
    # 요청 정보 출력
    body = await request.json()
    print(body["messageInput"])
    print(body["selected_model"])

    # LLM 호출
    llm = ChatGoogleGenerativeAI(model=body["selected_model"], api_key=GOOGLE_API)
    result = llm.invoke(body["messageInput"])
    print("LLM Result:", result.content)

    return {"response": result.content}

# 엔트로픽 모델 리스트 가져오기
@test_router.post("/getModelList")
async def getModelList(request: Request):
    client = anthropic.Anthropic(api_key=CLAUDE_API)

    result = client.models.list(limit=20)
    print(result)
    return{"response": "엔트로픽 모델리스트 테스트", "models":result}


# 사용자 의도파악 프롬프트 예시
@test_router.post("/userInputPrompt")
async def userInputPrompt(request: Request):
    body = await request.json()
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        streaming=False,
        openai_api_key=OPENAI_API
    )

    template = """
    다음은 사용자가 보낸 요청입니다:
    "{input}"

    위 요청을 분석해서 아래 JSON 형식으로만 답변하세요:
    {{
        "language": "...",
        "domain": "...",
        "complexity": "...",
        "accuracyImportance": "...",
        "recommendedModel": "..."
    }}
    """

    prompt = PromptTemplate(
        input_variables=["input"],
        template=template
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke({"input": body["messageInput"]})
    # print(response)
    return {"response": response}


# Rag 파일업로드 요청
@test_router.post("/uploadRAG")
async def uploadRAG(request: Request, file: UploadFile = File(...)):
    form_data = await request.form()
    project_id = form_data.get("project_id")
    user_email = form_data.get("user_email")
    session_id = form_data.get("session_id")
    print(form_data)
    print(file.filename)

    return {"filename": file.filename}


# 로그인
@test_router.post("/MSPLogin")
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
# @test_router.post("/MSPSocialLogin")
# async def MSPSocialLogin(request: Request):
#     body = await request.json()
#     print(body)
#
#     return {"response":"소셜 로그인 성공"}

@test_router.post("/MSPSocialLogin")
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



# 이메일 인증 요청
@test_router.post("/MSPSendEmail")
async def MSPSendEmail(request: Request):
    body = await request.json()
    print(body)
    email = body.get("email")
    secretCode = body.get("secretCode")

    return JSONResponse(content={"response": "이메일 확인 후 인증번호를 입력해주세요", "result": True}, status_code=200)

    subject = "이메일 인증 코드"
    body = f"귀하의 인증 코드는 {body["secretCode"]}입니다."
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = config.SENDER_EMAIL, email, subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        server.sendmail(config.SENDER_EMAIL, email, msg.as_string())
        server.quit()
        return JSONResponse(content={"response": "중복확인 되었습니다! 인증번호를 입력해주세요.", "result":True}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'response': f'이메일 전송 실패 : {str(e)}', "result":False}, status_code=500)




# 이메일 중복체크 요청
@test_router.post("/MSPCheckEmail")
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
@test_router.post("/MSPRegister")
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