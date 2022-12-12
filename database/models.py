from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base


BaseModel = declarative_base()


class UserModel(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    registration_date = Column(DateTime, server_default=func.now())

