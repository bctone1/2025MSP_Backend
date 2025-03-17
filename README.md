## 세팅 
CORE 모듈의 config.py에서 모든 API KEY, DB 접속 정보, 이메일 인증 정보 등을 설정합니다.
```
DB = 'postgresql'
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_SERVER = 'localhost'
DB_PORT = '5432'
DB_NAME = 'msp_database'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'MY ADDRESS'
SENDER_PASSWORD = 'MY KEY'

CLAUDE_API = "ANTHROPIC KEY"
GPT_API = "OPEN AI KEY"

```

## 실행 방법 
main.py를 
Pycharm 환경에서 작업 시 녹색 화살표 버튼을 클릭하면 실행됩니다.
### main.py
```
from fastapi import FastAPI
from api.routers import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용, 실제 운영 환경에서는 특정 도메인만 허용하는 것이 좋음
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

## 2025-03-13 작업 내용
FastAPI 구조에 맞게 전체 디렉터리 및 코드 구조를 변경 중입니다.
또한 CORE와 DATABASE 디렉터리에서 중요한 정보와 DB 관련 함수들을 정의해서,
실제 엔드 포인트 코드들을 최대한 간소화하는 작업 중에 있습니다.

현재 USER 관련 기능은 성공적으로 실행되며,
프로젝트랑 LLM은 아직 새로운 구조로 변경하는 작업 중에 있습니다.

![img.png](not_using/img.png)

아직 새로운 코드 구조로 변경하지 못한 코드들은 not_using 디렉터리에 전부 주석 처리 후 보관 중입니다.


## 2025-03-14 변경 사항
주요 변경 사항은 되도록 https://supermind.bctone.kr/c/ai-dev/ 에 작성 후 링크를 남기겠습니다.
### Alembic 기반 Migration 설정
https://supermind.bctone.kr/c/ai-dev/msp-backend-migration
해당 작업 진행 중 base.py, session.py, models 모듈의 init.py에도 약간의 변경 사항이 생겼습니다.
### Pydantic 스키마 구현
https://supermind.bctone.kr/c/ai-dev/msp-1f17f9
## 2025-03-17 변경 사항
https://supermind.bctone.kr/c/ai-dev/msp-crud
CRUD 디렉터리를 생성하여, 엔드포인트 정의 시 사용할 함수들을 미리 정의했습니다.
또한 기존 디렉터리 구조에 LangChain 디렉터리가 추가되었습니다.

![img_1.png](not_using/img_1.png)

아직 프로젝트 엔드포인트 코드가 제대로 작성되지 않았기 때문에 LangChain 작업은 이 작업이 끝난 뒤에 바로 시작할 예정입니다.
기존 provider.py로 정리하려던 구조는 전부 langchain.py로 대체될 것 같습니다.
![img.png](not_using/imgㅈ.png)
이제 localhost:5000/redoc 에서 USER 관련된 모든 엔드포인트 테스트 가능합니다.