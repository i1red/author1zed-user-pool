from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

BaseModel = declarative_base()


class UserModel(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    registration_date = Column(DateTime, server_default=func.now())


class ClientAppModel(BaseModel):
    __tablename__ = "client_app"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, unique=True)
    client_secret = Column(String)
    redirect_uris: list["RedirectUriModel"] = relationship("RedirectUriModel")


class RedirectUriModel(BaseModel):
    __tablename__ = "redirect_uri"

    id = Column(Integer, primary_key=True)
    uri = Column(String)
    client_id = Column(Integer, ForeignKey("client_app.id", ondelete="CASCADE"))
