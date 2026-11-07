"""Fetcher for the Open-Meteo Marine API (swell, waves, water temperature)."""

from datetime import UTC, datetime
from typing import Any

import httpx

from surfreport.models import MarineForecast, MarineHour

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
SOURCE_NAME = "open-meteo-marine"

# Open-Meteo hourly variable name -> MarineHour field name.
HEIGHT_VARIABLES: dict[str, str] = {
    "wave_height": "wave_height_ft",
    "swell_wave_height": "swell_height_ft",
    "secondary_swell_wave_height": "secondary_swell_height_ft",
    "wind_wave_height": "wind_wave_height_ft",
}
PLAIN_VARIABLES: dict[str, str] = {
    "wave_direction": "wave_direction_deg",
    "wave_period": "wave_period_s",
    "swell_wave_direction": "swell_direction_deg",
    "swell_wave_period": "swell_period_s",
    "secondary_swell_wave_direction": "secondary_swell_direction_deg",
    "secondary_swell_wave_period": "secondary_swell_period_s",
}
TEMPERATURE_VARIABLE = "sea_surface_temperature"
HOURLY_VARIABLES: list[str] = [
    *HEIGHT_VARIABLES,
    *PLAIN_VARIABLES,
    TEMPERATURE_VARIABLE,
]

METERS_TO_FEET = 3.28084


class OpenMeteoError(Exception):
    """Raised when Open-Meteo cannot be reached or returns unusable data."""


async def fetch_marine_forecast(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    timezone: str = "America/Los_Angeles",
) -> MarineForecast:
    """Fetch an hourly marine forecast for a point.

    Args:
        client: Shared async HTTP client.
        latitude: Latitude of the point, in decimal degrees.
        longitude: Longitude of the point, in decimal degrees.
        forecast_days: Number of days to forecast, including today.
        timezone: IANA time zone used for the returned hour timestamps.

    Returns:
        The parsed forecast, with heights in feet and water temperature in
        Fahrenheit.

    Raises:
        OpenMeteoError: If the request fails or the response is malformed.
    """
    params: dict[str, str | int | float] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(HOURLY_VARIABLES),
        "length_unit": "imperial",
        "forecast_days": forecast_days,
        "timezone": timezone,
    }
    try:
        response = await client.get(MARINE_URL, params=params, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise OpenMeteoError(f"Open-Meteo request failed: {exc}") from exc
    except ValueError as exc:
        raise OpenMeteoError("Open-Meteo returned invalid JSON") from exc
    return parse_marine_response(payload, fetched_at=datetime.now(UTC))


def parse_marine_response(
    payload: dict[str, Any], fetched_at: datetime
) -> MarineForecast:
    """Convert a raw Open-Meteo Marine response into a MarineForecast.

    Units are read from ``hourly_units`` so the parser works whether the
    response is metric or imperial.

    Args:
        payload: Decoded JSON body from the Marine API.
        fetched_at: When the data was fetched, stored with the forecast.

    Returns:
        The parsed forecast.

    Raises:
        OpenMeteoError: If required keys are missing.
    """
    try:
        hourly: dict[str, list[Any]] = payload["hourly"]
        times: list[str] = hourly["time"]
        forecast_meta = {
            "latitude": payload["latitude"],
            "longitude": payload["longitude"],
            "timezone": payload["timezone"],
        }
    except (KeyError, TypeError) as exc:
        raise OpenMeteoError(f"Open-Meteo response missing {exc}") from exc

    units: dict[str, str] = payload.get("hourly_units", {})
    height_factor = 1.0 if units.get("wave_height", "ft") == "ft" else METERS_TO_FEET
    temp_in_celsius = units.get(TEMPERATURE_VARIABLE, "°C") != "°F"

    hours = [
        MarineHour(
            time=datetime.fromisoformat(time),
            **{
                field: _scaled(_value_at(hourly, variable, index), height_factor)
                for variable, field in HEIGHT_VARIABLES.items()
            },
            **{
                field: _value_at(hourly, variable, index)
                for variable, field in PLAIN_VARIABLES.items()
            },
            water_temp_f=_to_fahrenheit(
                _value_at(hourly, TEMPERATURE_VARIABLE, index), temp_in_celsius
            ),
        )
        for index, time in enumerate(times)
    ]
    return MarineForecast(
        source=SOURCE_NAME, fetched_at=fetched_at, hours=hours, **forecast_meta
    )


def _value_at(hourly: dict[str, list[Any]], variable: str, index: int) -> float | None:
    try:
        value = hourly[variable][index]
    except KeyError, IndexError:
        return None
    return None if value is None else float(value)


def _scaled(value: float | None, factor: float) -> float | None:
    return None if value is None else round(value * factor, 2)


def _to_fahrenheit(value: float | None, is_celsius: bool) -> float | None:
    if value is None:
        return None
    return round(value * 9 / 5 + 32, 1) if is_celsius else value
