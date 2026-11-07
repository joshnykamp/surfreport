"""Database configuration, engine and table definitions."""

import os
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DatabaseConfigError(Exception):
    """Raised when the database connection is not configured."""


def database_url() -> str:
    """Read the database URL from the environment.

    Returns:
        The SQLAlchemy URL, e.g.
        ``postgresql+psycopg://surf:surf@localhost:5432/surfreport``.

    Raises:
        DatabaseConfigError: If ``DATABASE_URL`` is not set.
    """
    try:
        return os.environ["DATABASE_URL"]
    except KeyError as exc:
        raise DatabaseConfigError(
            "DATABASE_URL is not set. Copy .env.example to .env and run "
            "commands with `uv run --env-file .env ...`."
        ) from exc


def create_engine(url: str | None = None) -> AsyncEngine:
    """Create an async engine.

    Args:
        url: Database URL. Defaults to ``DATABASE_URL`` from the environment.

    Returns:
        A new async engine.
    """
    return create_async_engine(url or database_url())


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Build a session factory bound to an engine.

    Args:
        engine: The engine sessions should use.

    Returns:
        A factory producing ``AsyncSession`` objects.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all tables."""


class MarineSnapshot(Base):
    """A raw marine forecast exactly as fetched from a source.

    Every prediction will reference the snapshots it was made from, so
    predictions can later be compared with observations and replayed.
    """

    __tablename__ = "marine_snapshots"
    __table_args__ = (
        Index(
            "ix_marine_snapshots_location_time", "latitude", "longitude", "fetched_at"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
