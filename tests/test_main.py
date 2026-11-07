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


NWS_HOURLY = {
    "properties": {
        "periods": [
            {
                "startTime": "2026-11-07T06:00:00-08:00",
                "temperature": 58,
                "temperatureUnit": "F",
                "windSpeed": "5 to 10 mph",
                "windDirection": "NE",
                "shortForecast": "Sunny",
            }
        ]
    }
}


def nws_handler(request: httpx.Request) -> httpx.Response:
    """Answer NWS ``/points`` and hourly forecast requests.

    Args:
        request: The outgoing request.

    Returns:
        A canned response for the requested endpoint.
    """
    if request.url.path.startswith("/points/"):
        hourly = "https://api.weather.gov/gridpoints/LOX/1,1/forecast/hourly"
        return httpx.Response(200, json={"properties": {"forecastHourly": hourly}})
    return httpx.Response(200, json=NWS_HOURLY)


def test_wind_returns_forecast(use_upstream: Callable[[Handler], None]) -> None:
    use_upstream(nws_handler)

    response = TestClient(app).get("/wind")

    assert response.status_code == 200
    hour = response.json()["hours"][0]
    assert hour["wind_direction"] == "NE"
    assert hour["wind_speed_kt"] == 8.7


def test_wind_returns_502_when_upstream_fails(
    use_upstream: Callable[[Handler], None],
) -> None:
    use_upstream(lambda request: httpx.Response(503))

    response = TestClient(app).get("/wind")

    assert response.status_code == 502


def test_tides_returns_predictions(use_upstream: Callable[[Handler], None]) -> None:
    payload = {"predictions": [{"t": "2026-11-07 09:41", "v": "5.874", "type": "H"}]}
    use_upstream(lambda request: httpx.Response(200, json=payload))

    response = TestClient(app).get("/tides")

    assert response.status_code == 200
    body = response.json()
    assert body["station"] == "9410580"
    assert body["points"][0]["kind"] == "high"


def test_tides_returns_502_on_api_error(
    use_upstream: Callable[[Handler], None],
) -> None:
    payload = {"error": {"message": "No Predictions data was found."}}
    use_upstream(lambda request: httpx.Response(200, json=payload))

    response = TestClient(app).get("/tides")

    assert response.status_code == 502


def test_tides_validates_interval() -> None:
    response = TestClient(app).get("/tides", params={"interval": "weekly"})

    assert response.status_code == 422
