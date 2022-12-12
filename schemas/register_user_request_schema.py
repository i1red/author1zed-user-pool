from pydantic import BaseModel


class RegisterUserRequestSchema(BaseModel):
    username: str
    email: str
    password: str
