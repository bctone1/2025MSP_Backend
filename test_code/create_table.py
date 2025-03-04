from sqlalchemy import create_engine
from models import Base  # 모델 설계 코드가 포함된 파일에서 Base 가져오기

# PostgreSQL 데이터베이스 URI
DATABASE_URL = "postgresql://postgres:3636@localhost:5433/msp_database"

# 엔진 생성 및 테이블 생성
def create_table():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_table()
