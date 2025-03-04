from fastapi import FastAPI
from control_User.user_router import user_router
from project.project_router import project_router
from control_LLM.llm_router import llm_router
from fastapi.middleware.cors import CORSMiddleware

# uvicorn main:app --host 0.0.0.0 --port 5000    (터미널로 실행시킬 때)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용, 실제 운영 환경에서는 특정 도메인만 허용하는 것이 좋음
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)


app.include_router(user_router)
app.include_router(project_router)
app.include_router(llm_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI on port 5000!"}

