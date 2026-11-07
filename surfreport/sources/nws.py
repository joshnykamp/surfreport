"""Fetcher for the National Weather Service hourly forecast (wind, air temp).

The NWS API needs two calls: ``/points`` maps a lat/lon to a forecast grid
and returns the URL of that grid's hourly forecast, which we then fetch.
A ``User-Agent`` header is required.
"""

import re
from datetime import UTC, datetime
from typing import Any

import httpx

from surfreport.models import WindForecast, WindHour

POINTS_URL = "https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}"
SOURCE_NAME = "nws-hourly"
DEFAULT_USER_AGENT = "surfreport/0.1 (open source surf forecast)"
MPH_TO_KNOTS = 0.868976
COMPASS_POINTS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]  # fmt: skip


class NwsError(Exception):
    """Raised when the NWS API cannot be reached or returns unusable data."""


async def fetch_wind_forecast(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
    user_agent: str = DEFAULT_USER_AGENT,
) -> WindForecast:
    """Fetch the hourly NWS forecast for a point.

    Args:
        client: Shared async HTTP client.
        latitude: Latitude of the point, in decimal degrees.
        longitude: Longitude of the point, in decimal degrees.
        user_agent: Value for the required ``User-Agent`` header.

    Returns:
        The hourly forecast, with wind in knots and air temperature in
        Fahrenheit.

    Raises:
        NwsError: If either request fails or a response is malformed.
    """
    headers = {"User-Agent": user_agent, "Accept": "application/geo+json"}
    url = POINTS_URL.format(latitude=latitude, longitude=longitude)
    try:
        points = await client.get(url, headers=headers, timeout=10.0)
        points.raise_for_status()
        hourly_url: str = points.json()["properties"]["forecastHourly"]
        hourly = await client.get(hourly_url, headers=headers, timeout=10.0)
        hourly.raise_for_status()
        payload = hourly.json()
    except httpx.HTTPError as exc:
        raise NwsError(f"NWS request failed: {exc}") from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise NwsError(f"Unexpected NWS response: {exc}") from exc
    return parse_hourly_forecast(
        payload, latitude, longitude, fetched_at=datetime.now(UTC)
    )


def parse_hourly_forecast(
    payload: dict[str, Any],
    latitude: float,
    longitude: float,
    fetched_at: datetime,
) -> WindForecast:
    """Convert an NWS hourly forecast response into a WindForecast.

    Args:
        payload: Decoded JSON body of the ``forecast/hourly`` endpoint.
        latitude: Latitude the forecast was requested for.
        longitude: Longitude the forecast was requested for.
        fetched_at: When the data was fetched.

    Returns:
        The parsed forecast.

    Raises:
        NwsError: If required keys are missing.
    """
    try:
        periods: list[dict[str, Any]] = payload["properties"]["periods"]
        hours = [_hour_from_period(period) for period in periods]
    except (KeyError, TypeError, ValueError) as exc:
        raise NwsError(f"NWS forecast missing or malformed: {exc}") from exc
    return WindForecast(
        source=SOURCE_NAME,
        latitude=latitude,
        longitude=longitude,
        fetched_at=fetched_at,
        hours=hours,
    )


def _hour_from_period(period: dict[str, Any]) -> WindHour:
    low, high = parse_wind_speed_kt(period.get("windSpeed"))
    direction = period.get("windDirection") or None
    return WindHour(
        time=datetime.fromisoformat(period["startTime"]),
        wind_speed_kt=high,
        wind_speed_low_kt=low,
        wind_direction=direction,
        wind_direction_deg=compass_to_degrees(direction),
        air_temp_f=_fahrenheit(
            period.get("temperature"), period.get("temperatureUnit")
        ),
        short_forecast=period.get("shortForecast"),
    )


def parse_wind_speed_kt(text: str | None) -> tuple[float | None, float | None]:
    """Parse an NWS wind speed string such as ``"5 to 10 mph"`` into knots.

    Args:
        text: The ``windSpeed`` value from a forecast period.

    Returns:
        ``(low, high)`` in knots; equal for a single value, both None if the
        text has no numbers.
    """
    numbers = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", text or "")]
    if not numbers:
        return None, None
    return (
        round(min(numbers) * MPH_TO_KNOTS, 1),
        round(max(numbers) * MPH_TO_KNOTS, 1),
    )


def compass_to_degrees(direction: str | None) -> float | None:
    """Convert a 16 point compass direction to degrees.

    Args:
        direction: e.g. ``"WSW"``. Wind direction is where it blows from.

    Returns:
        Degrees from north, or None if the direction is unknown.
    """
    try:
        return COMPASS_POINTS.index((direction or "").upper()) * 22.5
    except ValueError:
        return None


def _fahrenheit(value: float | None, unit: str | None) -> float | None:
    if value is None:
        return None
    return round(float(value) * 9 / 5 + 32, 1) if unit == "C" else float(value)
