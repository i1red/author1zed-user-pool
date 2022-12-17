import dataclasses


@dataclasses.dataclass
class AuthCodeData:
    client_id: str
    user_id: int
