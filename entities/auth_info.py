import dataclasses


@dataclasses.dataclass
class AuthInfo:
    client_id: str
    redirect_uri: str
    state: str
