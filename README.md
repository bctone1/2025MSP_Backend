## 세팅 
### config.py 
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

### 패키지 설치
```
pip install -r requirements.txt
```

## DB 마이그레이션
### Alembic 설치 확인
```
alembic --version
```
해당 명령어로 설치 확인 후, 설치가 제대로 안 되었을 시에는
```
pip install alembic
```
수동 설치

### 마이그레이션 파일 생성
```
alembic revision --autogenerate -m "2025-03-19"
```

### Alembic 적용
```
alembic upgrade head
```
### PG VECTOR 관련 에러 해결 방법 ( 예시 )
Alembic이 생성한 versions 폴더의 가장 최신 코드에 Vector 관련 설정을 적용합니다.
```
from pgvector.sqlalchemy import Vector # PG VECTOR를 임포트합니다.

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('project_info_base', 'vector_memory',
               existing_type=postgresql.ARRAY(sa.INTEGER()), 
               type_=Vector(dim=1536), # 타입을 VECTOR(dim=1536)으로 변경합니다.
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('project_info_base', 'vector_memory',
               existing_type=Vector(dim=1536), # #타입을 Vector(dim=1536)으로 변경합니다.
               type_=postgresql.ARRAY(sa.INTEGER()),
               existing_nullable=True)
```
### alembic upgrade head 실행 시 오류
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 03930cf2be1a, 2025-03-19
Traceback (most recent call last):
  File "/home/bctone/meta-llm-msp/backend/venv/lib/python3.10/site-packages/sqlalchemy/engine/base.py", line 1964, in _exec_single_context
    self.dialect.do_execute(
  File "/home/bctone/meta-llm-msp/backend/venv/lib/python3.10/site-packages/sqlalchemy/engine/default.py", line 942, in do_execute
    cursor.execute(statement, parameters)
psycopg2.errors.DuplicateTable: relation "provider_table" already exists
...
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "provider_table" already exists

[SQL:
CREATE TABLE provider_table (
        id SERIAL NOT NULL,
        name VARCHAR(255) NOT NULL,
        status VARCHAR(50),
        website VARCHAR(255),
        description TEXT,
        PRIMARY KEY (id),
        UNIQUE (name)
)

]
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

