from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from database.session import get_db_connection, get_db
from schemas.project import *
from crud.project import *
from service.sms.make_code import generate_verification_code
import core.config as config
import os

project_router = APIRouter()

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

        print(f"created: {created_project.project_id}")
        return created_project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@project_router.post("/projectsList")
async def projects_list(request: Request):
    body = await request.json()
    email = body.get('email')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if email!='admin':
                    cur.execute(
                        'SELECT * FROM project_table WHERE LOWER(user_email) = %s ORDER BY project_id DESC',
                        (email,)
                    )
                else:
                    cur.execute('SELECT * FROM project_table  ORDER BY project_id DESC')

                column_names = [desc[0] for desc in cur.description]
                result = [dict(zip(column_names, row)) for row in cur.fetchall()]

                if not result:
                    return JSONResponse(content={"message": "프로젝트가 없습니다."}, status_code=404)
                else :
                    return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@project_router.post("/providerList", response_model=ProviderListResponse)
async def projects_list(db: Session = Depends(get_db)):
    providers = get_provider(db = db)
    return providers

@project_router.post("/DeleteSession", response_model=DeleteSessionResponse)
async def delete_session_endpoint(request : DeleteSessionRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    delete_session(db = db, session_id = session_id)
    return JSONResponse(content={"message": "삭제 성공"})


@project_router.post("/DeleteFile", response_model=DeleteFileResponse)
async def delete_file_endpoint(request : DeleteFileRequest, db: Session = Depends(get_db)):
    infobase_id = request.file.id
    file_name = request.file.name
    project_id = request.activeProject.project_id
    print(f"✅ 파일 아이디 : {infobase_id}")
    print(f"✅ 파일 이름 : {file_name}")
    print(f"✅ 프로젝트 아이디 : {project_id}")
    if infobase_id:
        delete_infobase(db=db, infobase_id=infobase_id)
    else:
        print("There is no Infobase ID")
        select_and_delete_infobase(db=db, project_id=project_id, file_name=file_name)
    return JSONResponse(content={"message": "삭제 성공"})
