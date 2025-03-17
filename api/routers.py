from fastapi import APIRouter
from api.endpoints import user
from api.endpoints import project

router = APIRouter()

router.include_router(user.user_router)
router.include_router(project.project_router)