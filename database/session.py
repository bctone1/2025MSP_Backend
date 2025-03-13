import os
import core.config as config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2

database = config.DB
user = config.DB_USER
pw = config.DB_PASSWORD
server = config.DB_SERVER
port = config.DB_PORT
name = config.DB_NAME
DATABASE_URL = os.getenv('DATABASE_URL', f'{database}://{user}:{pw}@{server}:{port}/{name}')

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    return psycopg2.connect(
        host=server,
        dbname=name,
        user=user,
        password=pw,
        port=port,
    )
