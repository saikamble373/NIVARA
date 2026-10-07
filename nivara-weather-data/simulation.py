import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

# Home -> College route (Thane, Maharashtra)
ROUTE_POINTS = [
    {"lat": 19.097930, "lng": 72.903440},
    {"lat": 19.1400, "lng": 72.9200},
    {"lat": 19.1850, "lng": 72.9350},
    {"lat": 19.2300, "lng": 72.9550},
    {"lat": 19.2662829, "lng": 72.9746964},
]

RISK_PROGRESSION = [
    {"score": 20, "level": "LOW"},
    {"score": 45, "level": "MODERATE"},
    {"score": 68, "level": "HIGH"},
    {"score": 85, "level": "CRITICAL"},
    {"score": 85, "level": "CRITICAL"},
]

def get_place_name(lat, lng):
    """Reverse geocode lat/lng to a real area name using OpenWeatherMap"""
    try:
        url = "https://api.openweathermap.org/geo/1.0/reverse"
        params = {"lat": lat, "lon": lng, "limit": 1, "appid": API_KEY}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data and len(data) > 0:
            name = data[0].get("name", "Unknown")
            state = data[0].get("state", "")
            return f"{name}, {state}" if state else name
        return "Unknown area"
    except Exception:
        return "Unknown area"

def get_simulated_position(step):
    """Returns GPS position + risk + real place name for a given step"""
    if step >= len(ROUTE_POINTS):
        step = len(ROUTE_POINTS) - 1

    position = ROUTE_POINTS[step]
    risk = RISK_PROGRESSION[step]
    place_name = get_place_name(position["lat"], position["lng"])

    return {
        "step": step,
        "lat": position["lat"],
        "lng": position["lng"],
        "place_name": place_name,
        "risk_score": risk["score"],
        "risk_level": risk["level"]
    }

def run_simulation(delay=2):
    """Simulates GPS movement through the route, step by step"""
    print("=== NIVARA Flood Simulation Started ===\n")
    for step in range(len(ROUTE_POINTS)):
        data = get_simulated_position(step)
        print(f"[Step {data['step']}] {data['place_name']}")
        print(f"  Location: ({data['lat']}, {data['lng']})")
        print(f"  Risk: {data['risk_score']}/100 - {data['risk_level']}")

        if data["risk_level"] == "CRITICAL":
            print("  ⚠️ ALERT: Switching to safer route recommended!\n")
        else:
            print()

        time.sleep(delay)

    print("=== Simulation Complete ===")

if __name__ == "__main__":
    run_simulation(delay=1)
