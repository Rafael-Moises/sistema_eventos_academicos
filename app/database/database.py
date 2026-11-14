
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não foi configurada no arquivo .env."
    )

SQL_ECHO = os.getenv("SQL_ECHO", "false").strip().lower() in (
    "true",
    "1",
    "yes"
)

engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass
