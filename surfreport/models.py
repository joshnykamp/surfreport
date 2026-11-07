"""Typed models shared by data sources, agents and the API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MarineHour(BaseModel):
    """Marine conditions for a single forecast hour.

    Heights are in feet, periods in seconds, directions in degrees the
    waves are coming from, and water temperature in Fahrenheit. Any field
    can be None when the source has no value for that hour.
    """

    time: datetime
    wave_height_ft: float | None = None
    wave_direction_deg: float | None = None
    wave_period_s: float | None = None
    swell_height_ft: float | None = None
    swell_direction_deg: float | None = None
    swell_period_s: float | None = None
    secondary_swell_height_ft: float | None = None
    secondary_swell_direction_deg: float | None = None
    secondary_swell_period_s: float | None = None
    wind_wave_height_ft: float | None = None
    water_temp_f: float | None = None


class BuoyReading(BaseModel):
    """One observation from a wave buoy.

    Heights are in feet, periods in seconds, directions in degrees the
    waves or wind are coming from, wind in knots and water temperature in
    Fahrenheit. Any field can be None when the buoy did not report it.
    """

    time: datetime
    wave_height_ft: float | None = None
    dominant_period_s: float | None = None
    average_period_s: float | None = None
    mean_direction_deg: float | None = None
    wind_direction_deg: float | None = None
    wind_speed_kt: float | None = None
    water_temp_f: float | None = None


class BuoyObservations(BaseModel):
    """Recent observations from one buoy station, newest first."""

    source: str
    station: str
    fetched_at: datetime
    readings: list[BuoyReading]


class MarineForecast(BaseModel):
    """An hourly marine forecast for one point, as returned by a source."""

    source: str
    latitude: float
    longitude: float
    timezone: str
    fetched_at: datetime
    hours: list[MarineHour]


class WindHour(BaseModel):
    """Forecast wind and weather for one hour.

    Wind speed is in knots and direction is where the wind blows from.
    ``wind_speed_kt`` is the top of the forecast range.
    """

    time: datetime
    wind_speed_kt: float | None = None
    wind_speed_low_kt: float | None = None
    wind_direction: str | None = None
    wind_direction_deg: float | None = None
    air_temp_f: float | None = None
    short_forecast: str | None = None


class WindForecast(BaseModel):
    """An hourly wind forecast for one point."""

    source: str
    latitude: float
    longitude: float
    fetched_at: datetime
    hours: list[WindHour]


class TidePoint(BaseModel):
    """A predicted tide height at one moment.

    ``kind`` is ``"high"`` or ``"low"`` for high and low tide predictions
    and None for hourly heights.
    """

    time: datetime
    height_ft: float
    kind: Literal["high", "low"] | None = None


class TideForecast(BaseModel):
    """Tide predictions for one station, in feet above the given datum."""

    source: str
    station: str
    datum: str
    interval: str
    fetched_at: datetime
    points: list[TidePoint]
