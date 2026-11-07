"""Tests for the NWS hourly wind fetcher."""

import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
import pytest

from surfreport.sources.nws import (
    NwsError,
    compass_to_degrees,
    fetch_wind_forecast,
    parse_hourly_forecast,
    parse_wind_speed_kt,
)

FETCHED_AT = datetime(2026, 11, 7, 20, 0, tzinfo=UTC)
HOURLY_URL = "https://api.weather.gov/gridpoints/LOX/160,30/forecast/hourly"
PACIFIC = timezone(timedelta(hours=-8))


@pytest.fixture
def hourly_payload() -> dict[str, Any]:
    """Load the saved NWS hourly forecast.

    Returns:
        The decoded JSON payload.
    """
    path = Path(__file__).parent / "fixtures" / "nws_hourly.json"
    payload: dict[str, Any] = json.loads(path.read_text())
    return payload


def points_response() -> dict[str, Any]:
    """Build a minimal ``/points`` response.

    Returns:
        A payload pointing at ``HOURLY_URL``.
    """
    return {"properties": {"forecastHourly": HOURLY_URL}}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("5 mph", (4.3, 4.3)),
        ("10 to 15 mph", (8.7, 13.0)),
        ("0 mph", (0.0, 0.0)),
        ("", (None, None)),
        (None, (None, None)),
    ],
)
def test_parse_wind_speed(
    text: str | None, expected: tuple[float | None, float | None]
) -> None:
    assert parse_wind_speed_kt(text) == expected


@pytest.mark.parametrize(
    ("direction", "degrees"),
    [
        ("N", 0.0),
        ("NE", 45.0),
        ("WSW", 247.5),
        ("nnw", 337.5),
        ("", None),
        (None, None),
    ],
)
def test_compass_to_degrees(direction: str | None, degrees: float | None) -> None:
    assert compass_to_degrees(direction) == degrees


def test_parse_hourly_forecast(hourly_payload: dict[str, Any]) -> None:
    forecast = parse_hourly_forecast(
        hourly_payload, 33.655, -118.005, fetched_at=FETCHED_AT
    )

    assert forecast.source == "nws-hourly"
    assert len(forecast.hours) == 3
    morning, afternoon, night = forecast.hours
    assert morning.time == datetime(2026, 11, 7, 6, 0, tzinfo=PACIFIC)
    assert morning.wind_direction == "NE"
    assert morning.wind_direction_deg == 45.0
    assert morning.wind_speed_kt == 4.3
    assert afternoon.wind_speed_low_kt == 8.7
    assert afternoon.wind_speed_kt == 13.0
    assert afternoon.air_temp_f == 68
    assert night.wind_direction is None
    assert night.wind_direction_deg is None


def test_parse_converts_celsius(hourly_payload: dict[str, Any]) -> None:
    period = hourly_payload["properties"]["periods"][0]
    period["temperature"], period["temperatureUnit"] = 20, "C"

    forecast = parse_hourly_forecast(
        hourly_payload, 33.655, -118.005, fetched_at=FETCHED_AT
    )

    assert forecast.hours[0].air_temp_f == 68.0


def test_parse_rejects_missing_periods() -> None:
    with pytest.raises(NwsError):
        parse_hourly_forecast({"properties": {}}, 0, 0, fetched_at=FETCHED_AT)


@pytest.mark.anyio
async def test_fetch_follows_points_to_hourly(hourly_payload: dict[str, Any]) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.startswith("/points/"):
            return httpx.Response(200, json=points_response())
        return httpx.Response(200, json=hourly_payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        forecast = await fetch_wind_forecast(client, 33.655, -118.005)

    assert [str(r.url) for r in seen] == [
        "https://api.weather.gov/points/33.6550,-118.0050",
        HOURLY_URL,
    ]
    assert all("surfreport" in r.headers["User-Agent"] for r in seen)
    assert len(forecast.hours) == 3


@pytest.mark.anyio
async def test_fetch_raises_when_points_fails() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NwsError):
            await fetch_wind_forecast(client, 33.655, -118.005)


@pytest.mark.anyio
async def test_fetch_raises_on_unexpected_points_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"properties": {}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NwsError):
            await fetch_wind_forecast(client, 33.655, -118.005)
