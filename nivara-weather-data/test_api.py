from weather_service import get_weather
from hazard_zones import load_hazard_zones
from simulation import run_simulation

def test_all():
    print("=== Testing Weather Service ===")
    weather = get_weather(19.097930, 72.903440)
    print(weather)
    print()

    print("=== Testing Hazard Zones ===")
    zones = load_hazard_zones()
    print(f"Loaded {len(zones['features'])} zones")
    for f in zones["features"]:
        print(f"- {f['properties']['name']}: {f['properties']['risk_level']}")
    print()

    print("=== Testing Simulation (quick, no delay) ===")
    run_simulation(delay=0.5)

if __name__ == "__main__":
    test_all()
