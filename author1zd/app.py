import os
import uuid
from typing import Final, Literal

from fastapi import HTTPException, FastAPI, Form, Query, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from author1zd.database.abstract.repositories.client_repository import ClientRepository
from author1zd.database.abstract.repositories.user_repository import UserRepository
from author1zd.database.exceptions import NonUniqueUserDataException
from author1zd.dependencies.database import create_user_repository, create_client_repository
from author1zd.dependencies.key_value_storage import (
    create_auth_info_collection,
    create_auth_code_collection,
    create_refresh_token_collection,
)
from author1zd.entities.user import User
from author1zd.objects.auth_code_data import AuthCodeData
from author1zd.objects.auth_info import AuthInfo
from author1zd.key_value_storage.abstract.collections.string_set import StringSet
from author1zd.key_value_storage.abstract.collections.string_to_dataclass_map import StringToDataclassMap
from author1zd.services.client import (
    ClientNotRegisteredException,
    RedirectUriNotAllowedException,
    SecretMismatchException,
    check_client_secret,
    check_redirect_uri,
)
from author1zd.settings import JwtSettings, settings_provider
from author1zd.services.token import generate_token_pair, get_refresh_token_claims
from author1zd.utility.password import verify_password, hash_password
from author1zd.utility.url import set_query_params

BASE_DIR: Final[str] = os.path.dirname(os.path.realpath(__file__))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/authorize", status_code=status.HTTP_302_FOUND)
async def authorize_view(
    response_type: Literal["code"],
    client_id: str,
    redirect_uri: str,
    state: str,
    client_repository: ClientRepository = Depends(create_client_repository),
    auth_info_collection: StringToDataclassMap[AuthInfo] = Depends(create_auth_info_collection),
):
    try:
        check_redirect_uri(client_id, redirect_uri, client_repository)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except RedirectUriNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    auth_info_key = uuid.uuid4().hex
    auth_info_collection.save(auth_info_key, AuthInfo(client_id, redirect_uri, state))

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
    username: str = Form(),
    password: str = Form(),
    auth_info_key: str = Query(),
    user_repository: UserRepository = Depends(create_user_repository),
    auth_info_collection: StringToDataclassMap[AuthInfo] = Depends(create_auth_info_collection),
    auth_code_collection: StringToDataclassMap[AuthCodeData] = Depends(create_auth_code_collection),
):
    auth_info = auth_info_collection.get(auth_info_key)

    if auth_info is None:
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_message="Authentication time expired. Try again",
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    user = user_repository.get_by_username(username)

    if user is None or not verify_password(password, user.password_hash):
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_401_UNAUTHORIZED,
                error_message="Incorrect username or password",
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    auth_info_collection.remove(auth_info_key)

    authorization_code = uuid.uuid4().hex
    auth_code_collection.save(authorization_code, AuthCodeData(client_id=auth_info.client_id, user_id=user.id))

    return RedirectResponse(
        url=set_query_params(auth_info.redirect_uri, code=authorization_code, state=auth_info.state),
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
    user_repository: UserRepository = Depends(create_user_repository),
    auth_info_collection: StringToDataclassMap[AuthInfo] = Depends(create_auth_info_collection),
    auth_code_collection: StringToDataclassMap[AuthCodeData] = Depends(create_auth_code_collection),
):
    auth_info = auth_info_collection.get(auth_info_key)

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
        user = user_repository.save(User.create(username, email, hash_password(password)))
    except NonUniqueUserDataException as e:
        return RedirectResponse(
            url=set_query_params(
                "/authentication_error",
                error_code=status.HTTP_409_CONFLICT,
                error_message=str(e),
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    auth_info_collection.remove(auth_info_key)

    authorization_code = uuid.uuid4().hex
    auth_code_collection.save(authorization_code, AuthCodeData(client_id=auth_info.client_id, user_id=user.id))

    return RedirectResponse(
        url=set_query_params(auth_info.redirect_uri, code=authorization_code, state=auth_info.state),
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
    client_repository: ClientRepository = Depends(create_client_repository),
    user_repository: UserRepository = Depends(create_user_repository),
    auth_code_collection: StringToDataclassMap[AuthCodeData] = Depends(create_auth_code_collection),
    refresh_token_collection: StringSet = Depends(create_refresh_token_collection),
    jwt_settings: JwtSettings = Depends(settings_provider(JwtSettings)),
):
    try:
        check_client_secret(client_id, client_secret, client_repository)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SecretMismatchException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    auth_code_data = auth_code_collection.get(code)
    if auth_code_data is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Code expired")

    if client_id != auth_code_data.client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client id")

    auth_code_collection.remove(code)

    user = user_repository.get_by_id(auth_code_data.user_id)

    return generate_token_pair(client_id, user, refresh_token_collection, jwt_settings)


@app.post("/refresh")
async def token_refresh_view(
    grant_type: Literal["refresh_token"] = Form(),
    client_id: str = Form(),
    client_secret: str = Form(),
    refresh_token: str = Form(),
    client_repository: ClientRepository = Depends(create_client_repository),
    user_repository: UserRepository = Depends(create_user_repository),
    refresh_token_collection: StringSet = Depends(create_refresh_token_collection),
    jwt_settings: JwtSettings = Depends(settings_provider(JwtSettings)),
):
    try:
        check_client_secret(client_id, client_secret, client_repository)
    except ClientNotRegisteredException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except SecretMismatchException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not refresh_token_collection.contains(refresh_token):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Token expired")

    refresh_token_claims = get_refresh_token_claims(refresh_token, jwt_settings)

    if client_id != refresh_token_claims.client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client id")

    refresh_token_collection.remove(refresh_token)

    user = user_repository.get_by_id(int(refresh_token_claims.sub))

    return generate_token_pair(client_id, user, refresh_token_collection, jwt_settings)
