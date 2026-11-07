"""Typed models shared by data sources, agents and the API."""

from datetime import datetime

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


class MarineForecast(BaseModel):
    """An hourly marine forecast for one point, as returned by a source."""

    source: str
    latitude: float
    longitude: float
    timezone: str
    fetched_at: datetime
    hours: list[MarineHour]
