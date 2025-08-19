from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from database.session import get_db
from schemas.project import *
from crud.project import *

project_router = APIRouter(prefix="/project", tags=["project"])

# =======================================
# 프로젝트 생성
# - Request: CreateProjectRequest
# - CRUD: create_new_project()
# =======================================
@project_router.post('/createproject')
async def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    name = request.projectInfo.project_name
    desc = request.projectInfo.description
    category = request.projectInfo.category
    model = request.projectInfo.model
    user_email = request.projectInfo.user_email
    provider = request.projectInfo.provider

    try:
        created_project = create_new_project(db, name, desc, category, model, user_email, provider)
        if created_project is None:
            raise HTTPException(status_code=500, detail="프로젝트 생성 실패")
        return created_project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =======================================
# 사용자별 프로젝트 목록 조회
# - Request: ProjectListRequest
# - Response: List[ProjectListResponse]
# =======================================
@project_router.post("/projectsList", response_model=List[ProjectListResponse])
async def projects_list(request: ProjectListRequest, db: Session = Depends(get_db)):
    email = request.email
    if not email:
        raise HTTPException(status_code=400, detail="이메일이 필요합니다.")

    try:
        result = get_project_list(db, email)
        if not result:
            return JSONResponse(content={"message": "프로젝트가 없습니다."}, status_code=404)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# =======================================
# Provider 목록 조회
# - Response: ProviderListResponse
# =======================================
@project_router.post("/providerList", response_model=ProviderListResponse)
async def projects_list(db: Session = Depends(get_db)):
    providers = get_provider(db=db)
    return providers


# =======================================
#  세션 삭제
# - Request: DeleteSessionRequest
# - CRUD: delete_session()
# =======================================
@project_router.post("/DeleteSession", response_model=DeleteSessionResponse)
async def delete_session_endpoint(request: DeleteSessionRequest, db: Session = Depends(get_db)):
    delete_session(db=db, session_id=request.session_id)
    return JSONResponse(content={"message": "삭제 성공"})


# =======================================
#  파일 삭제
# - Request: DeleteFileRequest
# - infobase_id 있으면 delete_infobase()
# - 없으면 select_and_delete_infobase()
# =======================================
@project_router.post("/DeleteFile", response_model=DeleteFileResponse)
async def delete_file_endpoint(request: DeleteFileRequest, db: Session = Depends(get_db)):
    infobase_id = request.file.id
    file_name = request.file.name
    project_id = request.activeProject.project_id
    if infobase_id:
        delete_infobase(db=db, infobase_id=infobase_id)
    else:
        print("There is no Infobase ID")
        select_and_delete_infobase(db=db, project_id=project_id, file_name=file_name)
    return JSONResponse(content={"message": "삭제 성공"})


# =======================================
#  프로젝트 삭제
# - Request: DeleteProjectRequest
# - 여러 개 project_ids 삭제 가능
# =======================================
@project_router.post("/DeleteProject", response_model=DeleteProjectResponse)
async def delete_project_endpoint(request: DeleteProjectRequest, db: Session = Depends(get_db)):
    delete_project(db=db, project_ids=request.project_ids)
    return JSONResponse(content={"message": "삭제 성공"})
