from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    database_url = settings.resolved_database_url
    if not database_url:
        return None

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


engine = _build_engine()
SessionLocal = (
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    if engine is not None
    else None
)


def is_database_enabled() -> bool:
    return SessionLocal is not None


def _quote_mysql_identifier(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


def ensure_database_exists() -> bool:
    database_url = settings.resolved_database_url
    if not database_url:
        return False

    url = make_url(database_url)
    database_name = url.database
    if not database_name or not url.drivername.startswith("mysql"):
        return False

    server_url = URL.create(
        drivername=url.drivername,
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        query=url.query,
    )
    server_engine = create_engine(
        server_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    try:
        with server_engine.connect() as connection:
            connection.execute(
                text(
                    "CREATE DATABASE IF NOT EXISTS "
                    f"{_quote_mysql_identifier(database_name)} "
                    "DEFAULT CHARACTER SET utf8mb4 "
                    "DEFAULT COLLATE utf8mb4_unicode_ci"
                )
            )
    finally:
        server_engine.dispose()

    return True


def _ensure_user_auth_columns() -> None:
    if engine is None:
        return

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("users")}
    if "password_hash" in column_names:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL"))


def init_db() -> bool:
    if engine is None or not settings.database_auto_create_tables:
        return False

    ensure_database_exists()

    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_user_auth_columns()
    return True


@contextmanager
def optional_session_scope() -> Iterator[Session | None]:
    if SessionLocal is None:
        yield None
        return

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
