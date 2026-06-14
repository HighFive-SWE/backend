from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str | None = None) -> Engine:
    url = url or settings.database_url
    # sqlite needs check_same_thread off so the engine can be shared across the
    # threadpool fastapi runs sync routes on. no-op for postgres.
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


engine: Engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(eng: Engine = engine) -> None:
    # import models so every table is registered on Base.metadata before create.
    from db import models  # noqa: F401

    Base.metadata.create_all(eng)


@contextmanager
def session_scope(eng: Engine | None = None) -> Iterator[Session]:
    factory = SessionLocal if eng is None else sessionmaker(bind=eng, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def dump_schema_sql() -> str:
    """render the full schema as sqlite DDL — the canonical schema artifact."""
    from sqlalchemy.dialects import sqlite
    from sqlalchemy.schema import CreateIndex, CreateTable

    from db import models  # noqa: F401

    dialect = sqlite.dialect()
    chunks: list[str] = []
    for table in Base.metadata.sorted_tables:
        chunks.append(str(CreateTable(table).compile(dialect=dialect)).strip() + ";")
        for index in table.indexes:
            chunks.append(str(CreateIndex(index).compile(dialect=dialect)).strip() + ";")
    return "\n\n".join(chunks) + "\n"
