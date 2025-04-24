from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from database.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50))
    group = Column(String(100))
    register_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    phone_number = Column(String(20), unique=True)
    projects = relationship("Project", back_populates="user", lazy="dynamic")

