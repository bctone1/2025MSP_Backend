from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import logging
from fastapi import Request
from database import get_db
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date
from control_LLM.claude_generator import setproject_response
import psycopg2
from typing import List
from project.crudProject import create_project

project_router = APIRouter()


class ProjectInfo(BaseModel):
    name: str
    description: str
    purpose: str
    language: str
    framework: str
    team: List[str]
    llm: str
    useremail: str

class CreateProjectRequest(BaseModel):
    projectInfo: ProjectInfo

@project_router.post("/createproject")
def createproject(request:dict, db: Session = Depends(get_db)):

    name = request.get("projectInfo", {}).get("name")
    description = request.get("projectInfo", {}).get("description")
    purpose = request.get("projectInfo", {}).get("purpose")
    language = request.get("projectInfo", {}).get("language")
    framework = request.get("projectInfo", {}).get("framework")
    team = request.get("projectInfo", {}).get("team")
    llm = request.get("projectInfo", {}).get("llm")
    num_of_member = len(team)
    email = request.get("useremail")
    print(f"생성자 email : {email}")
    start_date = datetime.now().strftime("%Y-%m-%d")
    new_project = create_project(
        db=db,
        project_name=name,
        start_date=start_date,
        end_date="2062-12-30",
        description=description,
        requirements=f"{language}, {framework}",
        model_setting=llm,
        num_of_member=num_of_member,
        user_email=email
    )

    return {"message": "프로젝트가 생성되었습니다."}, 200


class RequirementsListRequest(BaseModel):
    project_id : int

@project_router.post('/requirementsList')
def requirementsList(request:RequirementsListRequest):
    project_id = request.project_id
    print(project_id)
    conn = psycopg2.connect(
        host='localhost',
        dbname='msp_database',
        user='postgres',
        password='3636',
        port='5433',
    )
    cur = conn.cursor()
    cur.execute('SELECT * FROM public."requirements" WHERE project_id = %s ORDER BY id desc', (project_id,))
    result = cur.fetchall()
    print(result)
    cur.close()
    conn.close()
    return JSONResponse(content=result, status_code=200)


class RequirementInfo(BaseModel):
    id: int
    project_id : int
    title : str
    description : str
    category : str
    priority : str
    status : str
    use_cases : str
    constraints : str

class SaveRequirementRequeset(BaseModel):
    project_id : int
    req : List[RequirementInfo]

@project_router.post('/saveRequirement')
def saveRequirement(request:SaveRequirementRequeset):
    project_id = request.project_id
    req = request.req
    print(project_id)
    print(req)
    return JSONResponse(content={"message": "저장되었습니다."})

logger = logging.getLogger("uvicorn.error")

class ProjectListRequest(BaseModel):
    email: str

@project_router.post("/projectsList")
async def projects_list(request: ProjectListRequest):
    email = request.email
    print(f"Received email: {email}")
    project_id = 0
    try:
        # 데이터베이스 연결
        with psycopg2.connect(
            host='localhost',
            dbname='msp_database',
            user='postgres',
            password='3636',
            port=5433
        ) as conn:
            with conn.cursor() as cur:
                print("Database connection established")

                # 현재 연결된 데이터베이스 이름 출력
                cur.execute("SELECT current_database();")
                db_name = cur.fetchone()
                print(f"Connected to database: {db_name[0]}")

                if project_id !=0:
                    cur.execute(
                        'SELECT * FROM public."project" WHERE LOWER(user_email) = %s and project_id =%s ORDER BY start_date desc',
                        (email, project_id))
                else:
                    cur.execute('SELECT * FROM public."project" WHERE LOWER(user_email) = %s ORDER BY start_date desc',
                                (email,))
                result = cur.fetchall()

                print(f"Query result: {result}")

                if not result:
                    return JSONResponse(content={"message": "No projects found"}, status_code=404)

                # 결과 반환 (datetime.date 타입을 문자열로 변환)
                # 결과 반환 (datetime.date 타입을 문자열로 변환)
                projects = [
                    {
                        "project_name": row[0],
                        "start_date": row[1].strftime('%Y-%m-%d') if isinstance(row[1], date) and row[
                            1] is not None else row[1],
                        "end_date": row[2].strftime('%Y-%m-%d') if isinstance(row[2], date) and row[2] is not None else
                        row[2],
                        "description": row[3],
                        "technologies": row[4],
                        "model": row[5],
                        "priority": row[6],
                        "project_id": row[7],
                        "email": row[8]
                    }
                    for row in result
                ]
                return JSONResponse(content=projects, status_code=200)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content={"error": "Unexpected error"}, status_code=500)