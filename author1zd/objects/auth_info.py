from dataclasses import dataclass


@dataclass
class AuthInfo:
    client_id: str
    redirect_uri: str
    state: str
