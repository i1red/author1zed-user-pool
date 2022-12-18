import datetime
from dataclasses import dataclass


@dataclass
class AccessTokenClaims:
    client_id: str
    email: str
    username: str
    sub: str
    exp: datetime.datetime
