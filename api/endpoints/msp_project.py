from typing import Dict, Any
from fastapi import APIRouter, Request,HTTPException,Depends

from crud.project import *
from database.session import get_db
from crud.msp_project import *
from schemas.msp_project import UserProjectsResponse

test_router = APIRouter(tags=["msp_project"], prefix="/MSP_PROJECT")


@test_router.post("/msp_create_project")
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


@test_router.post("/msp_read_user_project", response_model=UserProjectsResponse)
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

    # return {
    #     "user_id": user_id,
    #     "projects": projects
    # }


# @test_router.post("/msp_read_user_project")
# async def msp_read_user_project(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
#     body = await request.json()
#     user_id = body.get("user_id")
#     print(user_id)
#
#     # DB에서 프로젝트 가져오기
#     projects = get_projects_by_user(db, user_id)
#     for p in projects:
#         print(f"id: {p.id}, name: {p.name}, description: {p.description}, status: {p.status}, cost: {p.cost}")
#
#     return {
#         "user_id": user_id,
#         "projects": [p.__dict__ for p in projects]
#     }
#
#     projects = [
#         {
#             "id": "proj1",
#             "name": "파일분석하기",
#             "description": "PDF와 Excel 파일을 분석하여 인사이트 추출하는 AI 시스템",
#             "status": "진행중",
#             "cost": "$12.75",
#             "conversations": [
#                 {
#                     "id": "conv1",
#                     "title": "Q4 매출 데이터 심화 분석",
#                     "status": "active",
#                     "date": "2시간 전",
#                     "preview": "Q4 매출 데이터를 업로드하여 트렌드 분석과 예측 모델링을 진행하고 있습니다. 특히 지역별 성과 차이가 흥미롭네요...",
#                     "messages": 24
#                 },
#                 {
#                     "id": "conv2",
#                     "title": "경쟁사 비교 분석 요청",
#                     "status": "completed",
#                     "date": "어제",
#                     "preview": "업계 주요 경쟁사 3곳의 재무제표를 비교 분석하여 우리 회사의 포지셔닝을 확인했습니다.",
#                     "messages": 18
#                 },
#                 {
#                     "id": "conv3",
#                     "title": "초기 데이터 업로드 및 분석",
#                     "status": "completed",
#                     "date": "3일 전",
#                     "preview": "첫 번째 Excel 파일을 업로드하고 기본적인 데이터 구조 분석을 수행했습니다.",
#                     "messages": 12
#                 }
#             ],
#             "knowledge": [
#                 {"id": "kb1", "name": "Q4_Sales_Report.xlsx", "type": "Excel", "size": "2.4MB", "uploaded": "2일 전"},
#                 {"id": "kb2", "name": "Market_Analysis.pdf", "type": "PDF", "size": "1.8MB", "uploaded": "1주 전"},
#                 {"id": "kb3", "name": "Competitor_Data.csv", "type": "CSV", "size": "856KB", "uploaded": "3일 전"}
#             ]
#         },
#         {
#             "id": "proj2",
#             "name": "파일업로드 test",
#             "description": "다양한 파일 형식 업로드 및 처리 테스트",
#             "status": "진행중",
#             "cost": "$4.25",
#             "conversations": [
#                 {
#                     "id": "conv1",
#                     "title": "이미지 파일 업로드 테스트",
#                     "status": "active",
#                     "date": "30분 전",
#                     "preview": "PNG, JPG, SVG 파일들의 업로드 테스트를 진행하고 있습니다. 파일 크기 제한과 변환 옵션을 확인 중...",
#                     "messages": 8
#                 },
#                 {
#                     "id": "conv2",
#                     "title": "대용량 파일 처리 개선",
#                     "status": "completed",
#                     "date": "2일 전",
#                     "preview": "100MB 이상의 대용량 파일 처리 성능을 개선하기 위한 청크 업로드 방식을 구현했습니다.",
#                     "messages": 15
#                 }
#             ],
#             "knowledge": [
#                 {"id": "kb1", "name": "test_image.png", "type": "Image", "size": "3.2MB", "uploaded": "1시간 전"},
#                 {"id": "kb2", "name": "large_dataset.zip", "type": "Archive", "size": "45MB", "uploaded": "2일 전"}
#             ]
#         },
#         {
#             "id": "proj3",
#             "name": "사업계획서 작성",
#             "description": "AI 기반 사업계획서 자동 생성 시스템",
#             "status": "계획중",
#             "cost": "$5.50",
#             "conversations": [
#                 {
#                     "id": "conv1",
#                     "title": "사업계획서 초안 작성",
#                     "status": "completed",
#                     "date": "1시간 전",
#                     "preview": "AI 스타트업을 위한 사업계획서 초안을 작성했습니다. 시장 분석, 비즈니스 모델, 재무 계획이 포함되어 있습니다.",
#                     "messages": 22
#                 }
#             ],
#             "knowledge": [
#                 {"id": "kb1", "name": "Business_Template.docx", "type": "Document", "size": "1.2MB",
#                  "uploaded": "2시간 전"},
#                 {"id": "kb2", "name": "Market_Research.pdf", "type": "PDF", "size": "4.1MB", "uploaded": "1일 전"}
#             ]
#         }
#     ]
#     return {"projects": projects}