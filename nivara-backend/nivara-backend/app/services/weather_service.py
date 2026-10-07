"""
Weather service.

Integrated with OpenWeatherMap using the logic from nivara-weather-data.
"""
import json
import os
from datetime import datetime
import requests

from app.config import USE_FALLBACK_WEATHER_ON_FAILURE
from app.models.schemas import WeatherResponse, HourlyForecast

_FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fallback_weather.json")

# Load WEATHER_API_KEY from nivara-weather-data/.env if present
_ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "nivara-weather-data", ".env"))
if os.path.exists(_ENV_PATH):
    with open(_ENV_PATH, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                try:
                    key, val = line.strip().split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = val
                except ValueError:
                    pass

def _fallback_weather(lat: float, lng: float) -> WeatherResponse:
    with open(_FALLBACK_PATH, "r") as f:
        d = json.load(f)
    return WeatherResponse(
        lat=lat,
        lng=lng,
        rainfall_mm=d["rainfall_mm"],
        forecast_rainfall_mm=d["forecast_rainfall_mm"],
        temperature_c=d["temperature_c"],
        wind_kmph=d["wind_kmph"],
        precipitation_probability=d["precipitation_probability"],
        hourly=[HourlyForecast(**h) for h in d["hourly"]],
        source="fallback",
        fetched_at=datetime.utcnow().isoformat() + "Z",
    )


def get_live_weather(lat: float, lng: float) -> WeatherResponse:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("No WEATHER_API_KEY found, using fallback")
        if USE_FALLBACK_WEATHER_ON_FAILURE:
            return _fallback_weather(lat, lng)
        raise Exception("No WEATHER_API_KEY found")

    try:
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        current_params = {
            "lat": lat,
            "lon": lng,
            "appid": api_key,
            "units": "metric"
        }
        resp = requests.get(current_url, params=current_params, timeout=5)
        resp.raise_for_status()
        current_data = resp.json()

        rainfall_mm = current_data.get("rain", {}).get("1h", 0.0)
        temperature_c = current_data.get("main", {}).get("temp", 0.0)
        # OpenWeatherMap returns wind speed in m/s, convert to km/h
        wind_kmph = current_data.get("wind", {}).get("speed", 0.0) * 3.6

        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lng,
            "appid": api_key,
            "units": "metric"
        }
        forecast_resp = requests.get(forecast_url, params=forecast_params, timeout=5)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()

        hourly = []
        precipitation_probability = 0.0
        
        for entry in forecast_data.get("list", [])[:3]:  # next ~9 hours (3-hour intervals)
            time_str = entry.get("dt_txt", "").replace(" ", "T") + "Z"
            h_rain = entry.get("rain", {}).get("3h", 0.0)
            h_temp = entry.get("main", {}).get("temp", 0.0)
            h_prob = entry.get("pop", 0.0) * 100.0

            hourly.append(HourlyForecast(
                time=time_str,
                rainfall_mm=h_rain,
                temperature_c=h_temp,
                precipitation_probability=h_prob,
            ))
            
            if not precipitation_probability and h_prob > 0:
                precipitation_probability = h_prob

        forecast_rainfall_mm = max((h.rainfall_mm for h in hourly), default=rainfall_mm)

        return WeatherResponse(
            lat=lat,
            lng=lng,
            rainfall_mm=rainfall_mm,
            forecast_rainfall_mm=forecast_rainfall_mm,
            temperature_c=temperature_c,
            wind_kmph=wind_kmph,
            precipitation_probability=precipitation_probability,
            hourly=hourly,
            source="live",
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        print(f"Error fetching live weather: {e}")
        if USE_FALLBACK_WEATHER_ON_FAILURE:
            return _fallback_weather(lat, lng)
        raise
