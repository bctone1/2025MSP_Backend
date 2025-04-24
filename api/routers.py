from fastapi import APIRouter
from api.endpoints import user
from api.endpoints import project
from api.endpoints import mcp
from api.endpoints import llm

router = APIRouter()

router.include_router(user.user_router)
router.include_router(project.project_router)
router.include_router(langchian.langchain_router)
router.include_router(mcp.mcp_router)