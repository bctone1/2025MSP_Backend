import core.config as config
from datetime import datetime
from sqlalchemy.orm import Session
from models.project import ProjectInfoBase
from pgvector.sqlalchemy import Vector
import numpy as np

def upload_file(db: Session, project: int, email: str, url: str, vector: list):
    try:
        # 벡터를 PGVector 형식으로 변환
        vector = np.array(vector)  # 벡터를 numpy 배열로 변환
        vector = vector.flatten()  # 벡터를 1차원 배열로 변환
        print(f"Uploading vector of length {len(vector)}")

        # 새로운 파일을 추가
        new_file = ProjectInfoBase(
            project_id=project,
            user_email=email,
            file_url=url,
            vector_memory=vector,  # 벡터 값을 vector_memory 컬럼에 저장
            upload_at=datetime.utcnow()  # 업로드 시간 설정
        )

        # 데이터베이스에 추가 및 커밋
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        # 결과 반환
        print(f"Uploaded file with vector: {new_file.vector_memory}")
        return new_file

    except Exception as e:
        db.rollback()  # 에러 발생 시 롤백
        print(f"Error occurred: {str(e)}")
        raise e