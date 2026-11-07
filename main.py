"""FastAPI entry point. Run with ``uv run fastapi dev main.py``."""

from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query

from surfreport.models import MarineForecast
from surfreport.sources.open_meteo import OpenMeteoError, fetch_marine_forecast

HB_PIER_LATITUDE = 33.655
HB_PIER_LONGITUDE = -118.005

app = FastAPI(title="Surf Report")


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async HTTP client for the duration of a request.

    Yields:
        An open ``httpx.AsyncClient``.
    """
    async with httpx.AsyncClient() as client:
        yield client


@app.get("/health")
async def health() -> dict[str, str]:
    """Report that the service is running.

    Returns:
        A status payload.
    """
    return {"status": "ok"}


@app.get("/marine")
async def marine_forecast(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    latitude: Annotated[float, Query(ge=-90, le=90)] = HB_PIER_LATITUDE,
    longitude: Annotated[float, Query(ge=-180, le=180)] = HB_PIER_LONGITUDE,
    days: Annotated[int, Query(ge=1, le=16)] = 7,
) -> MarineForecast:
    """Return the raw hourly marine forecast for a point.

    Defaults to the Huntington Beach Pier.

    Args:
        client: Injected HTTP client.
        latitude: Latitude of the point.
        longitude: Longitude of the point.
        days: Number of forecast days.

    Returns:
        The hourly marine forecast.

    Raises:
        HTTPException: 502 if the upstream source fails.
    """
    try:
        return await fetch_marine_forecast(
            client, latitude=latitude, longitude=longitude, forecast_days=days
        )
    except OpenMeteoError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
