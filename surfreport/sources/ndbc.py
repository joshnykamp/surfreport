"""Fetcher for NOAA NDBC real time buoy observations.

NDBC publishes the last 45 days of observations for each station as a
whitespace separated text file. CDIP buoys are mirrored there under their
NDBC (WMO) id, e.g. Long Beach Channel CDIP 215 is NDBC 46256.
"""

from datetime import UTC, datetime

import httpx

from surfreport.models import BuoyObservations, BuoyReading

REALTIME_URL = "https://www.ndbc.noaa.gov/data/realtime2/{station}.txt"
SOURCE_NAME = "ndbc-realtime"
MISSING = "MM"
METERS_TO_FEET = 3.28084
MPS_TO_KNOTS = 1.94384

LONG_BEACH_CHANNEL = "46256"


class NdbcError(Exception):
    """Raised when NDBC cannot be reached or returns unusable data."""


async def fetch_buoy_observations(
    client: httpx.AsyncClient, station: str = LONG_BEACH_CHANNEL
) -> BuoyObservations:
    """Fetch recent observations for an NDBC station.

    Args:
        client: Shared async HTTP client.
        station: NDBC station id, e.g. ``"46256"``.

    Returns:
        Observations, newest first, in feet, seconds, knots and Fahrenheit.

    Raises:
        NdbcError: If the request fails or the file cannot be parsed.
    """
    try:
        response = await client.get(REALTIME_URL.format(station=station), timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise NdbcError(f"NDBC request for {station} failed: {exc}") from exc
    return parse_realtime_text(response.text, station, fetched_at=datetime.now(UTC))


def parse_realtime_text(
    text: str, station: str, fetched_at: datetime
) -> BuoyObservations:
    """Parse an NDBC ``realtime2`` standard meteorological text file.

    Args:
        text: Raw file contents. The first line holds column names.
        station: Station id the file belongs to.
        fetched_at: When the file was fetched.

    Returns:
        Parsed observations, in file order (newest first).

    Raises:
        NdbcError: If the header is missing or a row is malformed.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    try:
        columns = lines[0].lstrip("#").split()
    except IndexError as exc:
        raise NdbcError(f"NDBC file for {station} is empty") from exc

    readings = []
    for line in lines:
        if line.startswith("#"):
            continue
        row = dict(zip(columns, line.split(), strict=False))
        try:
            readings.append(_reading_from_row(row))
        except (KeyError, ValueError) as exc:
            raise NdbcError(f"Bad NDBC row for {station}: {line!r}") from exc

    return BuoyObservations(
        source=SOURCE_NAME, station=station, fetched_at=fetched_at, readings=readings
    )


def _reading_from_row(row: dict[str, str]) -> BuoyReading:
    time = datetime(
        int(row["YY"]),
        int(row["MM"]),
        int(row["DD"]),
        int(row["hh"]),
        int(row["mm"]),
        tzinfo=UTC,
    )
    return BuoyReading(
        time=time,
        wave_height_ft=_scaled(_number(row, "WVHT"), METERS_TO_FEET, 2),
        dominant_period_s=_number(row, "DPD"),
        average_period_s=_number(row, "APD"),
        mean_direction_deg=_number(row, "MWD"),
        wind_direction_deg=_number(row, "WDIR"),
        wind_speed_kt=_scaled(_number(row, "WSPD"), MPS_TO_KNOTS, 1),
        water_temp_f=_fahrenheit(_number(row, "WTMP")),
    )


def _number(row: dict[str, str], column: str) -> float | None:
    value = row.get(column, MISSING)
    return None if value == MISSING else float(value)


def _scaled(value: float | None, factor: float, digits: int) -> float | None:
    return None if value is None else round(value * factor, digits)


def _fahrenheit(celsius: float | None) -> float | None:
    return None if celsius is None else round(celsius * 9 / 5 + 32, 1)
