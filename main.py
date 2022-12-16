import uuid
from typing import Final, Literal

from fastapi import HTTPException, FastAPI, Form, Query
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database.client import (
    check_redirect_uri,
    ClientNotRegisteredException,
    RedirectUriNotAllowedException,
    check_client_secret,
    SecretMismatchException,
)
from database.user import (
    save_user,
    NonUniqueUserDataException,
    get_user_by_username,
    get_user_by_id,
)
from redis_data.authorization_code import (
    save_auth_code_data,
    AuthCodeData,
    get_auth_code_data,
    remove_auth_code,
)
from redis_data.auth_info import (
    save_auth_info,
    get_auth_info,
    AuthInfo,
    remove_auth_info,
)
from redis_data.refresh_token import check_if_refresh_token_exists, remove_refresh_token
from settings import JwtSettings
from utility.token import generate_token_pair
from utility.url import set_query_params

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


PASSWORD_CONTEXT: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/authorize", status_code=status.HTTP_302_FOUND)
async def authorize_view(
    response_type: Literal["code"], client_id: str, redirect_uri: str, state: str
):
    try:
        check_redirect_uri(client_id, redirect_uri)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except RedirectUriNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    auth_info_key = uuid.uuid4().hex
    save_auth_info(auth_info_key, AuthInfo(client_id, redirect_uri, state))

    return RedirectResponse(
        url=set_query_params("/login", auth_info_key=auth_info_key),
        status_code=status.HTTP_302_FOUND,
    )


@app.get("/login")
async def login_page_view(request: Request, auth_info_key: str):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "query_params": {"auth_info_key": auth_info_key}},
    )


@app.post("/login", status_code=status.HTTP_302_FOUND)
async def login_post_view(
    username: str = Form(), password: str = Form(), auth_info_key: str = Query()
):
    auth_info = get_auth_info(auth_info_key)

    if auth_info is None:
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_message="Authentication time expired. Try again",
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = get_user_by_username(username)

    if user is None or not PASSWORD_CONTEXT.verify(password, user.password_hash):
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_message="Incorrect username or password",
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    remove_auth_info(auth_info_key)

    authorization_code = uuid.uuid4().hex
    save_auth_code_data(
        authorization_code,
        AuthCodeData(client_id=auth_info.client_id, user_id=user.id),
    )

    return RedirectResponse(
        url=set_query_params(
            auth_info.redirect_uri, code=authorization_code, state=auth_info.state
        ),
        status_code=status.HTTP_302_FOUND,
    )


@app.get("/signup")
async def signup_page_view(request: Request, auth_info_key: str):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "query_params": {"auth_info_key": auth_info_key}},
    )


@app.post("/signup", status_code=status.HTTP_302_FOUND)
async def signup_post_view(
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    auth_info_key: str = Query(),
):
    auth_info = get_auth_info(auth_info_key)

    if auth_info is None:
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_message="Authentication time expired. Try again",
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    try:
        user = save_user(username, email, PASSWORD_CONTEXT.hash(password))
    except NonUniqueUserDataException as e:
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_409_CONFLICT,
                error_message=str(e),
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    remove_auth_info(auth_info_key)

    authorization_code = uuid.uuid4().hex
    save_auth_code_data(
        authorization_code,
        AuthCodeData(client_id=auth_info.client_id, user_id=user.id),
    )

    return RedirectResponse(
        url=set_query_params(
            auth_info.redirect_uri, code=authorization_code, state=auth_info.state
        ),
        status_code=status.HTTP_302_FOUND,
    )


@app.get("/authentication_error")
async def error_page_view(request: Request, error_code: int, error_message: str):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error_code": error_code, "error_message": error_message},
        status_code=error_code,
    )


@app.post("/token")
async def token_code_view(
    grant_type: Literal["authorization_code"] = Form(),
    client_id: str = Form(),
    client_secret: str = Form(),
    code: str = Form(),
):
    try:
        check_client_secret(client_id, client_secret)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SecretMismatchException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    auth_code_data = get_auth_code_data(code)
    if auth_code_data is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Code expired")

    remove_auth_code(code)

    user = get_user_by_id(auth_code_data.user_id)

    return generate_token_pair(client_id, user)


@app.post("/refresh")
async def token_refresh_view(
    grant_type: Literal["refresh_token"] = Form(),
    client_id: str = Form(),
    client_secret: str = Form(),
    refresh_token: str = Form(),
):
    try:
        check_client_secret(client_id, client_secret)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SecretMismatchException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not check_if_refresh_token_exists(refresh_token):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Token expired")

    jwt_settings = JwtSettings()
    refresh_token_claims = jwt.decode(
        refresh_token,
        jwt_settings.refresh_token_secret_key,
        algorithms=[jwt_settings.algorithm],
    )

    remove_refresh_token(refresh_token)

    user_id = int(refresh_token_claims["sub"])
    user = get_user_by_id(user_id)

    return generate_token_pair(client_id, user)
