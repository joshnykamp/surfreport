"""Tests for the NDBC buoy fetcher."""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from surfreport.sources.ndbc import (
    LONG_BEACH_CHANNEL,
    NdbcError,
    fetch_buoy_observations,
    parse_realtime_text,
)

FETCHED_AT = datetime(2026, 11, 7, 19, 0, tzinfo=UTC)
SAMPLE = (Path(__file__).parent / "fixtures" / "ndbc_46256.txt").read_text()


def test_parse_reads_rows_newest_first() -> None:
    observations = parse_realtime_text(SAMPLE, "46256", fetched_at=FETCHED_AT)

    assert observations.station == "46256"
    assert len(observations.readings) == 3
    latest = observations.readings[0]
    assert latest.time == datetime(2026, 11, 7, 18, 56, tzinfo=UTC)
    assert latest.wave_height_ft == 2.95
    assert latest.dominant_period_s == 15
    assert latest.average_period_s == 8.6
    assert latest.mean_direction_deg == 255
    assert latest.water_temp_f == 63.3


def test_parse_treats_mm_as_missing() -> None:
    observations = parse_realtime_text(SAMPLE, "46256", fetched_at=FETCHED_AT)

    empty = observations.readings[2]
    assert empty.wave_height_ft is None
    assert empty.water_temp_f is None
    assert observations.readings[0].wind_speed_kt is None


def test_parse_converts_wind_to_knots() -> None:
    text = SAMPLE.replace("18 56  MM   MM", "18 56 270  5.0", 1)

    latest = parse_realtime_text(text, "46256", fetched_at=FETCHED_AT).readings[0]

    assert latest.wind_direction_deg == 270
    assert latest.wind_speed_kt == 9.7


def test_parse_rejects_empty_file() -> None:
    with pytest.raises(NdbcError):
        parse_realtime_text("", "46256", fetched_at=FETCHED_AT)


def test_parse_rejects_malformed_row() -> None:
    with pytest.raises(NdbcError):
        parse_realtime_text(SAMPLE + "2026 xx 07\n", "46256", fetched_at=FETCHED_AT)


@pytest.mark.anyio
async def test_fetch_requests_station_file() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, text=SAMPLE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        observations = await fetch_buoy_observations(client, LONG_BEACH_CHANNEL)

    assert str(seen[0].url) == ("https://www.ndbc.noaa.gov/data/realtime2/46256.txt")
    assert len(observations.readings) == 3


@pytest.mark.anyio
async def test_fetch_raises_on_missing_station() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NdbcError):
            await fetch_buoy_observations(client, "00000")
