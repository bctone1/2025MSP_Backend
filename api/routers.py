from fastapi import APIRouter
from api.endpoints import user

router = APIRouter()

router.include_router(user.user_router)