"""Tests for the Open-Meteo Marine fetcher."""

import copy
from datetime import UTC, datetime
from typing import Any

import httpx
import pytest

from surfreport.sources.open_meteo import (
    MARINE_URL,
    OpenMeteoError,
    fetch_marine_forecast,
    parse_marine_response,
)

FETCHED_AT = datetime(2026, 11, 7, 8, 0, tzinfo=UTC)


def _client(handler: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=handler)


def test_parse_reads_all_hours(marine_payload: dict[str, Any]) -> None:
    forecast = parse_marine_response(marine_payload, fetched_at=FETCHED_AT)

    assert forecast.source == "open-meteo-marine"
    assert forecast.timezone == "America/Los_Angeles"
    assert len(forecast.hours) == 3
    first = forecast.hours[0]
    assert first.time == datetime(2026, 11, 7, 0, 0)
    assert first.swell_height_ft == 2.95
    assert first.swell_period_s == 14.2
    assert first.swell_direction_deg == 265
    assert first.secondary_swell_period_s == 16.0


def test_parse_converts_water_temp_to_fahrenheit(
    marine_payload: dict[str, Any],
) -> None:
    forecast = parse_marine_response(marine_payload, fetched_at=FETCHED_AT)

    assert forecast.hours[0].water_temp_f == 64.4


def test_parse_converts_metric_heights_to_feet(
    marine_payload: dict[str, Any],
) -> None:
    metric = copy.deepcopy(marine_payload)
    metric["hourly_units"]["wave_height"] = "m"
    metric["hourly"]["swell_wave_height"][0] = 1.0

    forecast = parse_marine_response(metric, fetched_at=FETCHED_AT)

    assert forecast.hours[0].swell_height_ft == 3.28


def test_parse_keeps_missing_values_as_none(
    marine_payload: dict[str, Any],
) -> None:
    del marine_payload["hourly"]["wind_wave_height"]

    forecast = parse_marine_response(marine_payload, fetched_at=FETCHED_AT)

    assert forecast.hours[2].secondary_swell_height_ft is None
    assert forecast.hours[0].wind_wave_height_ft is None


def test_parse_rejects_missing_hourly(marine_payload: dict[str, Any]) -> None:
    del marine_payload["hourly"]

    with pytest.raises(OpenMeteoError):
        parse_marine_response(marine_payload, fetched_at=FETCHED_AT)


@pytest.mark.anyio
async def test_fetch_sends_expected_params(marine_payload: dict[str, Any]) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=marine_payload)

    async with _client(httpx.MockTransport(handler)) as client:
        forecast = await fetch_marine_forecast(client, 33.655, -118.005)

    assert len(forecast.hours) == 3
    request = seen[0]
    assert str(request.url).startswith(MARINE_URL)
    assert request.url.params["latitude"] == "33.655"
    assert request.url.params["length_unit"] == "imperial"
    assert "swell_wave_period" in request.url.params["hourly"]


@pytest.mark.anyio
async def test_fetch_raises_on_server_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    async with _client(httpx.MockTransport(handler)) as client:
        with pytest.raises(OpenMeteoError):
            await fetch_marine_forecast(client, 33.655, -118.005)


@pytest.mark.anyio
async def test_fetch_raises_on_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    async with _client(httpx.MockTransport(handler)) as client:
        with pytest.raises(OpenMeteoError):
            await fetch_marine_forecast(client, 33.655, -118.005)
