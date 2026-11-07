# Test fixtures

Saved API responses so tests run offline.

`open_meteo_marine.json` follows the documented Open-Meteo Marine response shape with hand-written values. Replace it with a real capture when convenient:

```sh
curl -s "https://marine-api.open-meteo.com/v1/marine?latitude=33.655&longitude=-118.005&hourly=wave_height,swell_wave_height,secondary_swell_wave_height,wind_wave_height,wave_direction,wave_period,swell_wave_direction,swell_wave_period,secondary_swell_wave_direction,secondary_swell_wave_period,sea_surface_temperature&length_unit=imperial&forecast_days=1&timezone=America%2FLos_Angeles" \
  | python3 -m json.tool > tests/fixtures/open_meteo_marine.json
```

If you do, update the expected values in `tests/test_open_meteo.py`.
