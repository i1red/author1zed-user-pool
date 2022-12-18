from dataclasses import dataclass


@dataclass
class Client:
    id: int
    client_id: str
    client_secret: str
    redirect_uris: list[str]
