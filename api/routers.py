from fastapi import APIRouter
from api.endpoints import user
from api.endpoints import project
from api.endpoints import llm
from api.endpoints import agent

router = APIRouter()

router.include_router(user.user_router)
router.include_router(project.project_router)
router.include_router(llm.langchain_router)
router.include_router(agent.agent_router)


"""
### 각 파일 맨위에 선언해야 함
# endpoints/user.py
user_router = APIRouter(prefix="/user", tags=["user"])

# endpoints/project.py
project_router = APIRouter(prefix="/project", tags=["project"])

# endpoints/llm.py
langchain_router = APIRouter(prefix="/llm", tags=["llm"])

# endpoints/agent.py
agent_router = APIRouter(prefix="/agent", tags=["agent"])

"""