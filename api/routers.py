from fastapi import APIRouter
from api.endpoints import user
from api.endpoints import project
from api.endpoints import langchian

router = APIRouter()

router.include_router(user.user_router)
router.include_router(project.project_router)
router.include_router(langchian.langchain_router)