from sqlalchemy import Column, String, Text, ForeignKey, Integer, Date, JSON
from database import Base
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector


class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key = True)
    pw = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    group = Column(String, nullable = False)
    name = Column(String, nullable=False)
    role = Column(String, nullable = False)


class Project(Base):
    __tablename__ = "project"
    project_name = Column(String)
    start_date =Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    requirements = Column(String)
    model_setting = Column(String, nullable=False)
    num_of_member_ = Column(Integer)
    project_id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey("user.email"))


class TestSesssion(Base):
    __tablename__ = "testsession"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    content = Column(Text)
    role = Column(String)
    embedding = Column(Vector)

class DataBase(Base):
    __tablename__ = "database"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    description = Column(Text)
    table_name = Column(String)
    table_column = Column(ARRAY(Text))
    column_types = Column(ARRAY(Text))

class Session(Base):
    __tablename__ = "session"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.project_id"), nullable=False)
    role = Column(String)
    content = Column(Text)
    embedding = Column(Vector)