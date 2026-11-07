"""Tests for the NOAA CO-OPS tide fetcher."""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from surfreport.sources.coops import (
    DATAGETTER_URL,
    CoopsError,
    fetch_tide_predictions,
    parse_predictions,
)

FETCHED_AT = datetime(2026, 11, 7, 20, 0, tzinfo=UTC)


@pytest.fixture
def hilo_payload() -> dict[str, Any]:
    """Load the saved high and low tide predictions.

    Returns:
        The decoded JSON payload.
    """
    path = Path(__file__).parent / "fixtures" / "coops_hilo.json"
    payload: dict[str, Any] = json.loads(path.read_text())
    return payload


def test_parse_high_and_low(hilo_payload: dict[str, Any]) -> None:
    forecast = parse_predictions(hilo_payload, "9410580", "hilo", FETCHED_AT)

    assert forecast.datum == "MLLW"
    assert [p.kind for p in forecast.points] == ["low", "high", "low", "high"]
    high = forecast.points[1]
    assert high.time == datetime(2026, 11, 7, 9, 41, tzinfo=UTC)
    assert high.height_ft == 5.874
    assert forecast.points[2].height_ft == -0.213


def test_parse_hourly_has_no_kind() -> None:
    payload = {"predictions": [{"t": "2026-11-07 00:00", "v": "2.5"}]}

    forecast = parse_predictions(payload, "9410580", "h", FETCHED_AT)

    assert forecast.points[0].kind is None
    assert forecast.points[0].height_ft == 2.5


def test_parse_raises_on_api_error() -> None:
    payload = {"error": {"message": "No Predictions data was found."}}

    with pytest.raises(CoopsError, match="No Predictions"):
        parse_predictions(payload, "0000000", "hilo", FETCHED_AT)


def test_parse_raises_on_malformed_row() -> None:
    payload = {"predictions": [{"t": "not a time", "v": "1.0"}]}

    with pytest.raises(CoopsError):
        parse_predictions(payload, "9410580", "hilo", FETCHED_AT)


@pytest.mark.anyio
async def test_fetch_sends_expected_params(hilo_payload: dict[str, Any]) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=hilo_payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        forecast = await fetch_tide_predictions(client, begin=date(2026, 11, 7))

    params = seen[0].url.params
    assert str(seen[0].url).startswith(DATAGETTER_URL)
    assert params["station"] == "9410580"
    assert params["interval"] == "hilo"
    assert params["time_zone"] == "gmt"
    assert params["begin_date"] == "20261107"
    assert params["end_date"] == "20261113"
    assert len(forecast.points) == 4


@pytest.mark.anyio
async def test_fetch_raises_on_server_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(CoopsError):
            await fetch_tide_predictions(client)
