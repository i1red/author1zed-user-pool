import uuid
from typing import Final, Literal
from urllib.parse import urlencode

from fastapi import HTTPException, FastAPI, Form, Query
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database.client import check_redirect_uri, ClientNotRegisteredException, RedirectUriNotAllowedException
from database.user import save_user, NonUniqueUserDataException, get_user_by_username
from redis_data.authorization_code import save_auth_code_data, AuthCodeData
from redis_data.state import save_state_data, StateException, get_state_data, StateData

from schemas.register_user_request_schema import RegisterUserRequestSchema
from schemas.register_user_response_schema import RegisterUserResponseSchema

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


PASSWORD_CONTEXT: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/register", response_model=RegisterUserResponseSchema)
async def register_view(user: RegisterUserRequestSchema) -> RegisterUserResponseSchema:
    try:
        save_user(user.username, user.email, PASSWORD_CONTEXT.hash(user.password))
    except NonUniqueUserDataException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return RegisterUserResponseSchema(detail="Registered successfully")


@app.get("/authorize", status_code=status.HTTP_302_FOUND)
async def authorize_view(response_type: Literal["code"], client_id: str, redirect_uri: str, state: str):
    try:
        check_redirect_uri(client_id, redirect_uri)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RedirectUriNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        save_state_data(state, StateData(client_id, redirect_uri))
    except StateException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return RedirectResponse(url="/login?" + urlencode({"state": state}), status_code=status.HTTP_302_FOUND)


@app.get("/login")
async def login_page_view(request: Request, state: str):
    return templates.TemplateResponse("login.html", {"request": request, "query_params": {"state": state}})


@app.post("/login", status_code=status.HTTP_302_FOUND)
async def login_post_view(username: str = Form(), password: str = Form(), state: str = Query()):
    state_data = get_state_data(state)

    if state_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication time expired")

    user = get_user_by_username(username)

    if user is None or not PASSWORD_CONTEXT.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    authorization_code = uuid.uuid4().hex

    save_auth_code_data(authorization_code, AuthCodeData(client_id=state_data.client_id, user_id=user.id))

    return RedirectResponse(
        url=state_data.redirect_uri + "?" + urlencode({"code": authorization_code, "state": state}),
        status_code=status.HTTP_302_FOUND
    )
