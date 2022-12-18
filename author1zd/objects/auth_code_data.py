from dataclasses import dataclass


@dataclass
class AuthCodeData:
    client_id: str
    user_id: int
