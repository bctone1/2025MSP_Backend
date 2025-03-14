from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import database.base as base
import psycopg2

engine = create_engine(base.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    return psycopg2.connect(
        host=base.server,
        dbname=base.name,
        user=base.user,
        password=base.pw,
        port=base.port,
    )
