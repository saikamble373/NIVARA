"""
Hazard zone service.

Loads GeoJSON hazard polygons (owned/updated by Member 5 - Weather + Data +
Simulation) and answers two questions the risk engine needs:
  1. Is point (lat, lng) inside / near a hazard zone?  -> flood_exposure_score
  2. How close is the nearest river/drain?              -> river_proximity_score

Member 5 can simply overwrite app/data/mumbai_hazard_zones.geojson with a
better file (same schema) and nothing else needs to change.
"""
import json
import os
from shapely.geometry import shape, Point
from app.config import RIVER_PROXIMITY_MAX_KM
from app.models.schemas import HazardZone

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mumbai_hazard_zones.geojson")

_cache = {"zones": None, "shapes": None}


def _load():
    if _cache["zones"] is not None:
        return _cache["zones"], _cache["shapes"]

    with open(_DATA_PATH, "r") as f:
        geojson = json.load(f)

    zones = []
    shapes = []
    for feature in geojson["features"]:
        props = feature["properties"]
        geom = shape(feature["geometry"])
        zones.append(HazardZone(
            id=props["id"],
            name=props["name"],
            hazard_type=props["hazard_type"],
            severity=props["severity"],
            geometry=feature["geometry"],
        ))
        shapes.append(geom)

    _cache["zones"] = zones
    _cache["shapes"] = shapes
    return zones, shapes


def get_all_zones():
    zones, _ = _load()
    return zones


def _haversine_km(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def flood_exposure_for_point(lat: float, lng: float):
    """
    Returns (score_0_100, list_of_hazard_names_hit_or_near).
    Inside a polygon -> high score. Near one (<1km) -> decaying score.
    """
    zones, shapes = _load()
    point = Point(lng, lat)  # shapely uses (x=lng, y=lat)

    best_score = 0.0
    hit_names = []

    for zone, geom in zip(zones, shapes):
        if geom.contains(point):
            severity_bonus = {"high": 100, "moderate": 75, "low": 50}.get(zone.severity, 60)
            best_score = max(best_score, severity_bonus)
            hit_names.append(zone.name)
        else:
            # distance in degrees -> rough km conversion for a quick proximity decay
            dist_deg = geom.distance(point)
            dist_km = dist_deg * 111.0
            if dist_km <= 1.0:
                proximity_score = max(0.0, 60 * (1 - dist_km))
                if proximity_score > best_score:
                    best_score = proximity_score
                if dist_km <= 0.5:
                    hit_names.append(f"{zone.name} (nearby)")

    return round(min(best_score, 100.0), 1), hit_names


def river_proximity_for_point(lat: float, lng: float) -> float:
    """
    Simple placeholder: treats hazard-zone centroids near tidal/river-fed
    areas as proxy 'river points'. Member 5 can replace with a real river
    GeoJSON layer later using the same distance-decay formula.
    """
    zones, shapes = _load()
    if not shapes:
        return 0.0

    min_dist_km = min(
        _haversine_km(lat, lng, geom.centroid.y, geom.centroid.x) for geom in shapes
    )
    if min_dist_km >= RIVER_PROXIMITY_MAX_KM:
        return 0.0
    return round(100.0 * (1 - min_dist_km / RIVER_PROXIMITY_MAX_KM), 1)
