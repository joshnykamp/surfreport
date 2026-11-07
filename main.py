"""FastAPI entry point. Run with ``uv run fastapi dev main.py``."""

from collections.abc import AsyncIterator
from typing import Annotated, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query

from surfreport.models import (
    BuoyObservations,
    MarineForecast,
    TideForecast,
    WindForecast,
)
from surfreport.sources.coops import NEWPORT_BEACH, CoopsError, fetch_tide_predictions
from surfreport.sources.ndbc import (
    LONG_BEACH_CHANNEL,
    NdbcError,
    fetch_buoy_observations,
)
from surfreport.sources.nws import NwsError, fetch_wind_forecast
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


@app.get("/buoy")
async def buoy_observations(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    station: Annotated[str, Query(pattern=r"^[0-9A-Za-z]{5}$")] = LONG_BEACH_CHANNEL,
    limit: Annotated[int, Query(ge=1, le=500)] = 24,
) -> BuoyObservations:
    """Return recent observations from an NDBC buoy, newest first.

    Defaults to Long Beach Channel (NDBC 46256, CDIP 215).

    Args:
        client: Injected HTTP client.
        station: NDBC station id.
        limit: Maximum number of readings to return.

    Returns:
        The latest readings from the station.

    Raises:
        HTTPException: 502 if NDBC fails.
    """
    try:
        observations = await fetch_buoy_observations(client, station)
    except NdbcError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return observations.model_copy(update={"readings": observations.readings[:limit]})


@app.get("/wind")
async def wind_forecast(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    latitude: Annotated[float, Query(ge=-90, le=90)] = HB_PIER_LATITUDE,
    longitude: Annotated[float, Query(ge=-180, le=180)] = HB_PIER_LONGITUDE,
) -> WindForecast:
    """Return the hourly NWS wind forecast for a point.

    Defaults to the Huntington Beach Pier. US locations only.

    Args:
        client: Injected HTTP client.
        latitude: Latitude of the point.
        longitude: Longitude of the point.

    Returns:
        The hourly wind forecast.

    Raises:
        HTTPException: 502 if the NWS API fails.
    """
    try:
        return await fetch_wind_forecast(client, latitude, longitude)
    except NwsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/tides")
async def tide_predictions(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    station: Annotated[str, Query(pattern=r"^[0-9]{7}$")] = NEWPORT_BEACH,
    interval: Literal["hilo", "h"] = "hilo",
    days: Annotated[int, Query(ge=1, le=31)] = 7,
) -> TideForecast:
    """Return tide predictions in feet above MLLW, with UTC times.

    Defaults to Newport Beach (CO-OPS 9410580), high and low tides only.

    Args:
        client: Injected HTTP client.
        station: CO-OPS station id.
        interval: ``hilo`` for high and low tides, ``h`` for hourly heights.
        days: Number of days to predict.

    Returns:
        The tide predictions.

    Raises:
        HTTPException: 502 if CO-OPS fails.
    """
    try:
        return await fetch_tide_predictions(
            client, station=station, days=days, interval=interval
        )
    except CoopsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
