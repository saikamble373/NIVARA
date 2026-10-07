import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

def get_fallback_weather():
    with open("data/sample_weather.json", "r") as f:
        return json.load(f)

def get_weather(lat, lng):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            print("Live API failed, using fallback data")
            return get_fallback_weather()

        return {
            "location": data["name"],
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "rainfall_mm": data.get("rain", {}).get("1h", 0)
        }
    except Exception as e:
        print(f"Error: {e}, using fallback data")
        return get_fallback_weather()

def get_forecast(lat, lng):
    """Returns hourly forecast with precipitation probability"""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lng,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("cod") != "200":
            print("Forecast API failed, using fallback")
            return []

        hourly_data = []
        for entry in data["list"][:8]:  # next 24 hours (3-hour intervals x 8)
            hourly_data.append({
                "datetime": entry["dt_txt"],
                "temp": entry["main"]["temp"],
                "rainfall_mm": entry.get("rain", {}).get("3h", 0),
                "precipitation_probability": entry.get("pop", 0) * 100,
                "condition": entry["weather"][0]["main"]
            })
        return hourly_data
    except Exception as e:
        print(f"Forecast error: {e}")
        return []

if __name__ == "__main__":
    data = get_weather(19.097930, 72.903440)
    print("=== Current Weather ===")
    print(data)

    print("\n=== 24-Hour Forecast ===")
    forecast = get_forecast(19.097930, 72.903440)
    for slot in forecast:
        print(slot)
