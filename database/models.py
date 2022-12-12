from typing import Final

from sqlalchemy import Table, Column, Integer, String, DateTime, func, MetaData

META_DATA: Final = MetaData()


users = Table(
    "users",
    META_DATA,
    Column("id", Integer, primary_key=True),
    Column("username", String(64), unique=True),
    Column("email", String, unique=True),
    Column("password_hash", String),
    Column("registration_date", DateTime, server_default=func.now())
)
