import datetime
from typing import Final

from fastapi import HTTPException, FastAPI
from passlib.context import CryptContext
from starlette import status

from database.user import save_user, NonUniqueUserDataException

from schemas.register_user_request_schema import RegisterUserRequestSchema
from schemas.register_user_response_schema import RegisterUserResponseSchema

app = FastAPI()


PASSWORD_CONTEXT: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/register", response_model=RegisterUserResponseSchema)
async def register_view(user: RegisterUserRequestSchema) -> RegisterUserResponseSchema:
    try:
        save_user(user.username, user.email, PASSWORD_CONTEXT.hash(user.password))
    except NonUniqueUserDataException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return RegisterUserResponseSchema(detail="Registered successfully")
