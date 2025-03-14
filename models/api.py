from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database.base import Base
from sqlalchemy.sql import func


class Provider(Base):
    __tablename__ = 'provider_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    status = Column(Text)
    website = Column(Text)
    description = Column(Text)

class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    key = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(20), nullable=False)
    environment = Column(String(50), nullable=False)
    usage_limit = Column(Integer, nullable=False)
    usage_count = Column(Integer, nullable=False, default=0)
    user_email = Column(String(255), nullable=False)

class TestTable(Base):
    __tablename__ = 'test_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)