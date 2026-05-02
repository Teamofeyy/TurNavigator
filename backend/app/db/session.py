from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _create_session_factory(database_url: str, *, echo: bool) -> sessionmaker[Session]:
    global _engine
    if _engine is not None:
        _engine.dispose()

    _engine = create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
    )
    return sessionmaker(
        bind=_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def configure_database(database_url: str | None = None) -> None:
    global _session_factory
    settings = get_settings()
    _session_factory = _create_session_factory(
        database_url or settings.resolved_database_url,
        echo=settings.sqlalchemy_echo,
    )


def get_engine() -> Engine:
    global _session_factory
    if _session_factory is None:
        configure_database()
    assert _engine is not None
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        configure_database()
    assert _session_factory is not None
    return _session_factory


class SessionFactoryProxy:
    def __call__(self, *args, **kwargs):
        return get_session_factory()(*args, **kwargs)


SessionLocal = SessionFactoryProxy()
engine = get_engine()


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
