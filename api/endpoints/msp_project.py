from typing import Dict, Any
from fastapi import APIRouter, Request,HTTPException,Depends


from crud.project import *
from database.session import get_db
from crud.msp_project import *
from schemas.msp_project import UserProjectsResponse

project_router = APIRouter(tags=["msp_project"], prefix="/MSP_PROJECT")


@project_router.post("/msp_create_project")
async def msp_create_project(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")
    name = body.get("name")
    category = body.get("category")
    description = body.get("description")
    status = body.get("status")
    cost = body.get("cost")

    # 필수값 체크
    if not user_id or not name:
        raise HTTPException(status_code=400, detail="user_id와 name은 필수입니다.")

    # ✅ CRUD 함수 호출
    new_project = create_project(
        db=db,
        user_id=user_id,
        name=name,
        category=category,
        description=description,
        status=status,
        cost=cost
    )

    return {
        "status":True,
        "response": f"{new_project.name} 프로젝트가 생성되었습니다. ",
        "project": {
            "id": new_project.id,
            "user_id": new_project.user_id,
            "name": new_project.name,
            "category": new_project.category,
            "description": new_project.description,
            "status": new_project.status,
            "cost": new_project.cost,
            "created_at": str(new_project.created_at)
        }
    }


@project_router.post("/msp_read_user_project", response_model=UserProjectsResponse)
async def msp_read_user_project(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    user_id = body.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id는 필수입니다.")

    projects = get_projects_by_user(db, user_id)

    return {
        "user_id": user_id,
        "projects": [serialize_project(p) for p in projects]
    }

