from pydantic import BaseModel


class RegisterUserResponseSchema(BaseModel):
    detail: str
