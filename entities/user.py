import datetime
from dataclasses import dataclass
from typing import TypeVar, Type

TUser = TypeVar("TUser", bound="User")


@dataclass
class User:
    id: int | None
    username: str
    email: str
    password_hash: str
    registration_date: datetime.datetime | None

    @classmethod
    def create(cls: Type[TUser], username: str, email: str, password_hash: str) -> TUser:
        return cls(id=None, username=username, email=email, password_hash=password_hash, registration_date=None)
