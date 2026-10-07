import json

def load_hazard_zones():
    with open("data/mumbai_hazards.geojson", "r") as f:
        data = json.load(f)
    return data

def get_zone_by_name(name):
    zones = load_hazard_zones()
    for feature in zones["features"]:
        if feature["properties"]["name"].lower() == name.lower():
            return feature
    return None

if __name__ == "__main__":
    zones = load_hazard_zones()
    print(f"Total hazard zones loaded: {len(zones['features'])}")
    for f in zones["features"]:
        print(f"- {f['properties']['name']}: {f['properties']['risk_level']}")
