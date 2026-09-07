from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def build_engine():
    settings = get_settings()
    return create_engine(
        settings.mysql_dsn,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=settings.mysql_pool_size,
        max_overflow=settings.mysql_max_overflow,
    )


def build_session_factory():
    return sessionmaker(bind=build_engine(), autoflush=False, expire_on_commit=False)


def check_mysql() -> None:
    with build_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
