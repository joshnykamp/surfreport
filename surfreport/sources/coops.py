"""Fetcher for NOAA CO-OPS tide predictions.

Heights are feet above MLLW (mean lower low water), the datum used on
tide charts. Times are requested in GMT so daylight saving changes never
make an hour ambiguous.
"""

from datetime import UTC, date, datetime, timedelta
from typing import Any, Literal

import httpx

from surfreport.models import TideForecast, TidePoint

DATAGETTER_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
SOURCE_NAME = "noaa-coops"
APPLICATION = "surfreport"
NEWPORT_BEACH = "9410580"
DATUM = "MLLW"

Interval = Literal["hilo", "h"]
KINDS: dict[str, Literal["high", "low"]] = {"H": "high", "L": "low"}


class CoopsError(Exception):
    """Raised when CO-OPS cannot be reached or returns unusable data."""


async def fetch_tide_predictions(
    client: httpx.AsyncClient,
    station: str = NEWPORT_BEACH,
    begin: date | None = None,
    days: int = 7,
    interval: Interval = "hilo",
) -> TideForecast:
    """Fetch tide predictions for a station.

    Args:
        client: Shared async HTTP client.
        station: CO-OPS station id, e.g. ``"9410580"`` (Newport Beach).
        begin: First day to predict (UTC). Defaults to today.
        days: Number of days to predict.
        interval: ``"hilo"`` for high and low tides, ``"h"`` for hourly
            heights.

    Returns:
        Tide predictions in feet above MLLW, with UTC times.

    Raises:
        CoopsError: If the request fails or CO-OPS returns an error.
    """
    start = begin or datetime.now(UTC).date()
    params: dict[str, str] = {
        "station": station,
        "product": "predictions",
        "datum": DATUM,
        "units": "english",
        "time_zone": "gmt",
        "interval": interval,
        "format": "json",
        "application": APPLICATION,
        "begin_date": start.strftime("%Y%m%d"),
        "end_date": (start + timedelta(days=days - 1)).strftime("%Y%m%d"),
    }
    try:
        response = await client.get(DATAGETTER_URL, params=params, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise CoopsError(f"CO-OPS request failed: {exc}") from exc
    except ValueError as exc:
        raise CoopsError("CO-OPS returned invalid JSON") from exc
    return parse_predictions(payload, station, interval, fetched_at=datetime.now(UTC))


def parse_predictions(
    payload: dict[str, Any],
    station: str,
    interval: Interval,
    fetched_at: datetime,
) -> TideForecast:
    """Convert a CO-OPS predictions response into a TideForecast.

    Args:
        payload: Decoded JSON body. CO-OPS reports errors with HTTP 200 and
            an ``error`` object instead of ``predictions``.
        station: Station id the predictions belong to.
        interval: Interval that was requested.
        fetched_at: When the data was fetched.

    Returns:
        The parsed predictions.

    Raises:
        CoopsError: If the payload is an error or is malformed.
    """
    if "error" in payload:
        message = payload["error"].get("message", "unknown error")
        raise CoopsError(f"CO-OPS error for {station}: {message}")
    try:
        points = [_point(row) for row in payload["predictions"]]
    except (KeyError, TypeError, ValueError) as exc:
        raise CoopsError(f"CO-OPS predictions malformed: {exc}") from exc
    return TideForecast(
        source=SOURCE_NAME,
        station=station,
        datum=DATUM,
        interval=interval,
        fetched_at=fetched_at,
        points=points,
    )


def _point(row: dict[str, str]) -> TidePoint:
    time = datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
    return TidePoint(
        time=time, height_ft=float(row["v"]), kind=KINDS.get(row.get("type", ""))
    )
