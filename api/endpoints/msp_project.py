from fastapi import APIRouter, Request,HTTPException,Depends
from crud.msp_project import *
from database.session import get_db
from crud.msp_project import create_project

test_router = APIRouter(tags=["msp_project"], prefix="/MSP_PROJECT")

@test_router.post("/msp_create_project")
async def msp_create_project(request: Request, db: Session = Depends(get_db)):
    # return {"response": "msp_create_project테스트연결"}
    """
      프로젝트 생성 API
      Body 예시:
      {
          "user_id": 1,
          "name": "테스트 프로젝트",
          "category": "AI",
          "description": "FastAPI 프로젝트 생성 테스트",
          "status": "active",
          "cost": "1000"
      }
      """
    body = await request.json()
    user_id = body.get("user_id")
    name = body.get("name")
    category = body.get("category")
    description = body.get("description")
    status = body.get("status")
    cost = body.get("cost")

    if not user_id or not name:
        raise HTTPException(status_code=400, detail="user_id와 name은 필수입니다.")


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
        "response": "프로젝트 생성 성공",
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



