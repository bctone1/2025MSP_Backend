# models/associations.py
from sqlalchemy import Table, Column, Integer, ForeignKey
from database.base import Base



# 따로 빼둔 이유: 순환 참조(Circular Import) 방지
# project.py → knowledge.py 를 import 하고,
# knowledge.py → project.py 를 import 하면
# 🚨 Python 이 두 파일을 동시에 로딩하다가 partially initialized module 에러가 발생합니다.



# 중간 테이블 (프로젝트 ↔ 지식 연결)
project_knowledge_association = Table(
    "_msp_project_knowledge_association",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("_msp_project_table.id", ondelete="CASCADE"), primary_key=True),
    Column("knowledge_id", Integer, ForeignKey("_msp_knowledge_table.id", ondelete="CASCADE"), primary_key=True)
)