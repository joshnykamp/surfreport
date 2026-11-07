"""Tests for the API endpoints."""

from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app, get_http_client

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture
def use_upstream() -> Iterator[Callable[[Handler], None]]:
    """Route the app's outbound HTTP calls to a mock handler.

    Yields:
        A function that installs a handler for the current test.
    """

    def install(handler: Handler) -> None:
        async def override() -> AsyncIterator[httpx.AsyncClient]:
            async with httpx.AsyncClient(
                transport=httpx.MockTransport(handler)
            ) as client:
                yield client

        app.dependency_overrides[get_http_client] = override

    yield install
    app.dependency_overrides.clear()


def test_health() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_marine_returns_forecast(
    use_upstream: Callable[[Handler], None], marine_payload: dict[str, Any]
) -> None:
    use_upstream(lambda request: httpx.Response(200, json=marine_payload))

    response = TestClient(app).get("/marine", params={"days": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "open-meteo-marine"
    assert len(body["hours"]) == 3
    assert body["hours"][0]["water_temp_f"] == 64.4


def test_marine_returns_502_when_upstream_fails(
    use_upstream: Callable[[Handler], None],
) -> None:
    use_upstream(lambda request: httpx.Response(503))

    response = TestClient(app).get("/marine")

    assert response.status_code == 502


BUOY_TEXT = """#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP
#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC
2026 11 07 18 56  MM   MM   MM   0.9    15   8.6 255     MM    MM  17.4
2026 11 07 18 26  MM   MM   MM   0.8    15   8.4 254     MM    MM  17.4
"""


def test_buoy_returns_latest_readings(
    use_upstream: Callable[[Handler], None],
) -> None:
    use_upstream(lambda request: httpx.Response(200, text=BUOY_TEXT))

    response = TestClient(app).get("/buoy", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["station"] == "46256"
    assert len(body["readings"]) == 1
    assert body["readings"][0]["dominant_period_s"] == 15


def test_buoy_returns_502_when_upstream_fails(
    use_upstream: Callable[[Handler], None],
) -> None:
    use_upstream(lambda request: httpx.Response(404))

    response = TestClient(app).get("/buoy")

    assert response.status_code == 502


def test_buoy_validates_station() -> None:
    response = TestClient(app).get("/buoy", params={"station": "../etc"})

    assert response.status_code == 422


def test_marine_validates_latitude() -> None:
    response = TestClient(app).get("/marine", params={"latitude": 200})

    assert response.status_code == 422
