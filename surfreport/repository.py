"""Read and write operations for stored data."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from surfreport.db import MarineSnapshot
from surfreport.models import MarineForecast


async def save_marine_snapshot(
    session: AsyncSession, forecast: MarineForecast
) -> MarineSnapshot:
    """Store a fetched marine forecast.

    The caller owns the transaction and must commit.

    Args:
        session: Open database session.
        forecast: The forecast to store.

    Returns:
        The stored row, with its id assigned.
    """
    snapshot = MarineSnapshot(
        source=forecast.source,
        latitude=forecast.latitude,
        longitude=forecast.longitude,
        fetched_at=forecast.fetched_at,
        payload=forecast.model_dump(mode="json"),
    )
    session.add(snapshot)
    await session.flush()
    return snapshot


async def latest_marine_forecast(
    session: AsyncSession, latitude: float, longitude: float
) -> MarineForecast | None:
    """Load the most recently fetched forecast for a point.

    Args:
        session: Open database session.
        latitude: Latitude the forecast was stored under.
        longitude: Longitude the forecast was stored under.

    Returns:
        The latest forecast, or None if nothing is stored for that point.
    """
    statement = (
        select(MarineSnapshot)
        .where(
            MarineSnapshot.latitude == latitude,
            MarineSnapshot.longitude == longitude,
        )
        .order_by(MarineSnapshot.fetched_at.desc())
        .limit(1)
    )
    snapshot = await session.scalar(statement)
    if snapshot is None:
        return None
    return MarineForecast.model_validate(snapshot.payload)
