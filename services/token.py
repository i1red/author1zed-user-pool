import datetime
from dataclasses import asdict

from jose import jwt

from entities.user import User
from key_value_storage.abstract.collections.string_set import StringSet
from objects.access_token_claims import AccessTokenClaims
from objects.refresh_token_claims import RefreshTokenClaims
from exchange_objects.token_pair import TokenPair
from settings import JwtSettings


def generate_token_pair(
    client_id: str, user: User, refresh_token_collection: StringSet, jwt_settings: JwtSettings
) -> TokenPair:
    access_token_claims = AccessTokenClaims(
        client_id=client_id,
        email=user.email,
        username=user.username,
        sub=str(user.id),
        exp=datetime.datetime.utcnow() + datetime.timedelta(seconds=jwt_settings.access_token_ttl),
    )
    access_token = jwt.encode(
        asdict(access_token_claims),
        key=jwt_settings.access_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )

    refresh_token_claims = RefreshTokenClaims(
        client_id=client_id,
        sub=str(user.id),
        exp=datetime.datetime.utcnow() + datetime.timedelta(seconds=jwt_settings.refresh_token_ttl),
    )
    refresh_token = jwt.encode(
        asdict(refresh_token_claims),
        key=jwt_settings.refresh_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )
    refresh_token_collection.save(refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_in=jwt_settings.access_token_ttl,
        refresh_token_expires_in=jwt_settings.refresh_token_ttl,
    )


def get_refresh_token_claims(refresh_token: str, jwt_settings: JwtSettings) -> RefreshTokenClaims:
    claims_dict = jwt.decode(
        refresh_token,
        jwt_settings.refresh_token_secret_key,
        algorithms=[jwt_settings.algorithm],
    )
    return RefreshTokenClaims(**claims_dict)
