from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from langchain_service.llms.setup import get_llm
from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import json
from database.session import get_db_connection, get_db
from schemas.project import *
from crud.project import *

project_router = APIRouter()
'''
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
    '''
'''
@project_router.post("/createproject")
def createproject(request:dict, db: Session = Depends(get_db)):

    name = request.get("projectInfo", {}).get("name")
    description = request.get("projectInfo", {}).get("description")
    purpose = request.get("projectInfo", {}).get("purpose")
    language = request.get("projectInfo", {}).get("language")
    framework = request.get("projectInfo", {}).get("framework")
    team = request.get("projectInfo", {}).get("team")
    llm = request.get("projectInfo", {}).get("llm")
    # print(llm)
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
'''



@project_router.post('/createproject', response_model=CreateProjectResponse)
async def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    name = request.projectInfo.name
    desc = request.projectInfo.desc
    category = request.projectInfo.category
    model = request.projectInfo.model
    user_email = request.projectInfo.user_email
    provider = request.projectInfo.provider

    print(f"Creating project: {name}, {desc}, {category}, {model}, {user_email}, {provider}")

    try:
        created_project = create_new_project(db, name, desc, category, model, user_email, provider)
        if created_project is None:
            raise HTTPException(status_code=500, detail="프로젝트 생성 실패")

        return CreateProjectResponse(
            message="프로젝트가 생성되었습니다",
        )
    except Exception as e:
        print(f"Unexpected error: {e}")  # 디버깅용 로그
        raise HTTPException(status_code=500, detail=str(e))

@project_router.post("/projectsList")
async def projects_list(request: Request):
    body = await request.json()
    print(body)
    email = body.get('email')

    print(f"Received email: {email}")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT * FROM project_table WHERE LOWER(user_email) = %s ORDER BY project_id DESC',
                    (email,)
                )

                column_names = [desc[0] for desc in cur.description]
                result = [dict(zip(column_names, row)) for row in cur.fetchall()]
                # result = cur.fetchall()

                print(f"Query result: {result}")

                if not result:
                    print("프로젝트 없음")
                    return JSONResponse(content={"message": "프로젝트가 없습니다."}, status_code=404)
                else :
                    return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@project_router.post("/providerList", response_model=ProviderListResponse)
async def projects_list(db: Session = Depends(get_db)):
    providers = get_provider(db = db)
    print(f"Providers : {providers}")
    # return JSONResponse(content={"data": providers}, status_code=200)
    return providers


'''
@project_router.post('/projectsList')
async def project_list(request: ProjectListRequest, db: Session = Depends(get_db)):
    email = request.email
    print(email)

'''
'''
class RequirementsListRequest(BaseModel):
    project_id : int


'''
'''
@project_router.post('/requirementsList')
def requirementsList(request:RequirementsListRequest):
    project_id = request.project_id
    print(project_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "requirements" WHERE project_id = %s ORDER BY id desc', (project_id,))
    column_names = [desc[0] for desc in cur.description]
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]
    print(result)
    cur.close()
    conn.close()
    return JSONResponse(content=result, status_code=200)

@project_router.post('/SystemSettingList')
async def SystemSettingList(request:Request):
    data = await request.json()  # 요청 데이터 가져오기
    project_id = data.get('project_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "systemSetting" WHERE project_id = %s ORDER BY id desc', (project_id,))

    column_names = [desc[0] for desc in cur.description]
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return JSONResponse(content=result, status_code=200)

@project_router.post('/datatables')
async def datatables(request:Request):
    data = await request.json()
    project_id = data.get('project_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "tabledata" WHERE project_id = %s ORDER BY id desc', (project_id,))

    column_names = [desc[0] for desc in cur.description]
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return JSONResponse(content=result, status_code=200)


@project_router.post('/apidata')
async def apidata(request:Request):
    data = await request.json()
    project_id = data.get('project_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "apitable" WHERE project_id = %s ORDER BY id desc', (project_id,))

    column_names = [desc[0] for desc in cur.description]
    result = [dict(zip(column_names, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return JSONResponse(content=result, status_code=200)



# class RequirementInfo(BaseModel):
#     id: int
#     project_id : int
#     title : str
#     description : str
#     category : str
#     priority : str
#     status : str
#     use_cases : str
#     constraints : str

# class SaveRequirementRequeset(BaseModel):
#     project_id : int
#     req : List[RequirementInfo]



@project_router.post('/deleteRequirement')
async def deleteRequirement(request: Request):
    data = await request.json()
    project_id = data.get('project_id')
    definition = data.get('req', {}).get('definition')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 데이터 확인
        check_query = "SELECT id FROM requirements WHERE definition = %s"
        cursor.execute(check_query, (definition,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            return JSONResponse(content={"message": "이미 삭제된 데이터입니다."})

        # 데이터 삭제
        delete_query = "DELETE FROM requirements WHERE definition = %s AND project_id = %s"
        cursor.execute(delete_query, (definition, project_id))
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "삭제되었습니다.."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@project_router.post('/saveRequirement')
async def saveRequirement(request: Request):
    data = await request.json()
    project_id = data.get('project_id')
    definition = data.get('req', {}).get('definition')
    description = data.get('req', {}).get('description')
    title = data.get('req', {}).get('title')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 중복 확인
        check_query = "SELECT id FROM requirements WHERE definition = %s"
        cursor.execute(check_query, (definition,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return JSONResponse(content={"message": "이미 추가된 데이터입니다."})

        # 데이터 삽입
        insert_query = """
            INSERT INTO requirements (project_id, definition, description, title)
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        cursor.execute(insert_query, (project_id, definition, description, title))
        inserted_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "저장되었습니다.", "id": inserted_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@project_router.post('/deleteSystemSetting')
async def deleteSystemSetting(request: Request):
    data = await request.json()
    project_id = data.get('project_id')
    definition = data.get('req', {}).get('definition')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 데이터 확인
        check_query = """
                SELECT id FROM "systemSetting" WHERE definition = %s
                """
        cursor.execute(check_query, (definition,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            return JSONResponse(content={"message": "이미 삭제된 데이터입니다."})

        # 데이터 삭제
        delete_query = """DELETE FROM "systemSetting" WHERE definition = %s AND project_id = %s"""
        cursor.execute(delete_query, (definition, project_id))
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "삭제되었습니다.."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@project_router.post('/saveSystemSetting')
async def saveSystemSetting(request:Request):
    data = await request.json()  # 요청 데이터 가져오기
    # print(data)

    project_id = data.get('project_id')
    definition = data.get('req', {}).get('definition')
    description = data.get('req', {}).get('description')
    title = data.get('req', {}).get('title')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 중복 확인
        check_query = """
        SELECT id FROM "systemSetting" WHERE definition = %s
        """
        cursor.execute(check_query, (definition,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return JSONResponse(content={"message": "이미 추가된 데이터입니다."})

        query = """
                        INSERT INTO "systemSetting" (project_id, definition, description, title)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """
        cursor.execute(query, (project_id, definition, description, title))
        inserted_id = cursor.fetchone()[0]  # 삽입된 id 가져오기
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "저장되었습니다.", "id": inserted_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@project_router.post('/deleteDatatable')
async def deleteDatatable(request: Request):
    data = await request.json()
    project_id = data.get('project_id')
    table_name = data.get('req', {}).get('table_name')
    columns = data.get('req', {}).get('columns')
    # columns 데이터가 딕셔너리이므로, 각 항목을 JSON 형식으로 직렬화
    jsoncolumns = [json.dumps(col, ensure_ascii=False) for col in columns]
    description = data.get('req', {}).get('description')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 데이터 확인
        check_query = """
                SELECT id FROM tabledata WHERE description = %s
                """
        cursor.execute(check_query, (description,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            return JSONResponse(content={"message": "이미 삭제된 데이터입니다."})

        # 데이터 삭제
        delete_query = """DELETE FROM tabledata WHERE description = %s AND project_id = %s"""
        cursor.execute(delete_query, (description, project_id))
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "삭제되었습니다.."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@project_router.post('/saveDatatable')
async def saveDatatable(request:Request):
    data = await request.json()  # 요청 데이터 가져오기

    project_id = data.get('project_id')
    table_name = data.get('req', {}).get('table_name')
    columns = data.get('req', {}).get('columns')
    # columns 데이터가 딕셔너리이므로, 각 항목을 JSON 형식으로 직렬화
    jsoncolumns = [json.dumps(col, ensure_ascii=False) for col in columns]
    description = data.get('req', {}).get('description')
    print(columns)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        check_query = """
                SELECT id FROM tabledata WHERE description = %s
                """
        cursor.execute(check_query, (description,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return JSONResponse(content={"message": "이미 추가된 데이터입니다."})


        query = """
                        INSERT INTO tabledata (project_id, table_name, columns, description)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """
        # JSON 배열 형태로 삽입
        cursor.execute(query, (project_id, table_name, jsoncolumns, description))

        inserted_id = cursor.fetchone()[0]  # 삽입된 id 가져오기

        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "저장되었습니다.", "id": inserted_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




@project_router.post('/deleteApidata')
async def deleteApidata(request: Request):
    data = await request.json()  # 요청 데이터 가져오기

    project_id = data.get('project_id')
    apidata = data.get('req', {}).get('apidata')
    jsonapidata = json.dumps(apidata, ensure_ascii=False)  # apidata를 JSON 문자열로 변환
    api_name = data.get('req', {}).get('api_name')
    description = data.get('req', {}).get('description')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 데이터 확인
        check_query = """
                SELECT id FROM apitable WHERE description = %s
                """
        cursor.execute(check_query, (description,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            return JSONResponse(content={"message": "이미 삭제된 데이터입니다."})

        # 데이터 삭제
        delete_query = """DELETE FROM apitable WHERE description = %s AND project_id = %s"""
        cursor.execute(delete_query, (description, project_id))
        conn.commit()
        conn.close()
        return JSONResponse(content={"message": "삭제되었습니다.."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@project_router.post('/saveApidata')
async def saveApidata(request:Request):
    data = await request.json()  # 요청 데이터 가져오기

    project_id = data.get('project_id')
    apidata = data.get('req', {}).get('apidata')
    jsonapidata = json.dumps(apidata, ensure_ascii=False)  # apidata를 JSON 문자열로 변환
    api_name = data.get('req', {}).get('api_name')
    description = data.get('req', {}).get('description')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        check_query = """
                        SELECT id FROM apitable WHERE description = %s
                        """
        cursor.execute(check_query, (description,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return JSONResponse(content={"message": "이미 추가된 데이터입니다."})

        query = """
                    INSERT INTO apitable (project_id, api_name, apidata, description)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """
        cursor.execute(query, (project_id, api_name, jsonapidata, description))  # JSON 문자열로 삽입

        inserted_id = cursor.fetchone()[0]  # 삽입된 id 가져오기

        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "저장되었습니다.", "id": inserted_id})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



logger = logging.getLogger("uvicorn.error")


@project_router.post("/projectsList")
async def projects_list(request: Request):
    body = await request.json()
    print(body)
    email = body.get('email')

    print(f"Received email: {email}")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT * FROM "project" WHERE LOWER(user_email) = %s ORDER BY project_id DESC',
                    (email,)
                )

                column_names = [desc[0] for desc in cur.description]
                result = [dict(zip(column_names, row)) for row in cur.fetchall()]
                # result = cur.fetchall()

                print(f"Query result: {result}")

                if not result:
                    print("프로젝트 없음")
                    return JSONResponse(content={"message": "프로젝트가 없습니다."}, status_code=404)
                else :
                    return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")



@project_router.post("/getmembers")
async def get_members():
    try:
        conn = get_db_connection()
        print("db_connected")
        cur = conn.cursor()

        cur.execute('SELECT * FROM user_table ORDER BY register_at desc')
        print("success")
        column_names = [desc[0] for desc in cur.description]
        result = [dict(zip(column_names, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()
        print(result)

        # 결과를 반환
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")'''