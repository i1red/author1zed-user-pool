import datetime
from dataclasses import dataclass


@dataclass
class RefreshTokenClaims:
    client_id: str
    sub: str
    exp: datetime.datetime
