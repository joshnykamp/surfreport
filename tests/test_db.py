"""Tests for database configuration and storage.

Tests marked ``postgres`` need a migrated local database:

    docker compose up -d
    uv run --env-file .env alembic upgrade head
    uv run --env-file .env pytest
"""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from surfreport.db import DatabaseConfigError, create_engine, database_url
from surfreport.repository import latest_marine_forecast, save_marine_snapshot
from surfreport.sources.open_meteo import parse_marine_response

needs_postgres = pytest.mark.skipif(
    "DATABASE_URL" not in os.environ,
    reason="DATABASE_URL not set; run with `uv run --env-file .env pytest`",
)


def test_database_url_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(DatabaseConfigError):
        database_url()


def test_database_url_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h/db")

    assert database_url() == "postgresql+psycopg://u:p@h/db"


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Open a session inside a transaction that is always rolled back.

    Yields:
        A session whose changes are discarded after the test.
    """
    engine = create_engine()
    async with engine.connect() as connection:
        transaction = await connection.begin()
        yield AsyncSession(bind=connection, expire_on_commit=False)
        await transaction.rollback()
    await engine.dispose()


@needs_postgres
@pytest.mark.anyio
async def test_snapshot_round_trip(
    session: AsyncSession, marine_payload: dict[str, Any]
) -> None:
    older = parse_marine_response(
        marine_payload, fetched_at=datetime(2026, 11, 6, tzinfo=UTC)
    )
    newer = parse_marine_response(
        marine_payload, fetched_at=datetime(2026, 11, 7, tzinfo=UTC)
    )

    await save_marine_snapshot(session, older)
    saved = await save_marine_snapshot(session, newer)
    loaded = await latest_marine_forecast(session, newer.latitude, newer.longitude)

    assert saved.id is not None
    assert loaded == newer


@needs_postgres
@pytest.mark.anyio
async def test_latest_returns_none_for_unknown_point(session: AsyncSession) -> None:
    assert await latest_marine_forecast(session, 0.0, 0.0) is None
