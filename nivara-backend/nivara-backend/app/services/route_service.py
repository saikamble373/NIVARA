"""
Route-risk service.

Takes a polyline (list of lat/lng points) from Member 3 (Maps + GPS +
Routing) and:
  1. checks each point against hazard zones,
  2. computes what % of the route is exposed,
  3. reuses the SAME risk_engine.calculate_risk() to get an overall score.

This is what powers "Home -> College, current route = HIGH, alternative =
LOW" in the roadmap's Hours 18-24 target.
"""
from typing import List, Optional
from app.models.schemas import Coordinates, RouteSegmentRisk, RouteRiskResult
from app.services import hazard_service, weather_service, risk_engine


def _analyze_route(route: List[Coordinates], weather, official_warning_level: str) -> RouteRiskResult:
    segments = []
    hit_count = 0

    for i in range(len(route) - 1):
        start, end = route[i], route[i + 1]
        mid_lat = (start.lat + end.lat) / 2
        mid_lng = (start.lng + end.lng) / 2
        exposure_score, hazard_names = hazard_service.flood_exposure_for_point(mid_lat, mid_lng)
        in_zone = exposure_score >= 60  # treat as "inside" for segment flagging
        if in_zone:
            hit_count += 1

        segments.append(RouteSegmentRisk(
            segment_index=i,
            start=start,
            end=end,
            in_hazard_zone=in_zone,
            hazard_names=hazard_names,
        ))

    route_exposure_pct = round(100.0 * hit_count / max(len(segments), 1), 1)

    # Use midpoint of the whole route for rainfall/river factors (good enough
    # for a 48hr prototype - route is usually within one weather cell)
    mid_idx = len(route) // 2
    mid_point = route[mid_idx]
    flood_exposure_score, _ = hazard_service.flood_exposure_for_point(mid_point.lat, mid_point.lng)
    river_score = hazard_service.river_proximity_for_point(mid_point.lat, mid_point.lng)

    risk = risk_engine.calculate_risk(
        lat=mid_point.lat,
        lng=mid_point.lng,
        rainfall_mm=weather.rainfall_mm,
        forecast_rainfall_mm=weather.forecast_rainfall_mm,
        flood_exposure_score=flood_exposure_score,
        official_warning_level=official_warning_level,
        route_exposure_pct=route_exposure_pct,
        river_proximity_score=river_score,
    )

    return RouteRiskResult(
        overall_score=risk.score,
        overall_level=risk.level,
        route_exposure_pct=route_exposure_pct,
        segments=segments,
        hazardous_segment_count=hit_count,
    )


def analyze(
    route: List[Coordinates],
    alt_route: Optional[List[Coordinates]],
    official_warning_level: str,
    auto_fetch_weather: bool,
):
    mid_point = route[len(route) // 2]
    weather = weather_service.get_live_weather(mid_point.lat, mid_point.lng) if auto_fetch_weather \
        else weather_service.get_live_weather(mid_point.lat, mid_point.lng)

    primary = _analyze_route(route, weather, official_warning_level)

    alternative = None
    recommendation = "Current route risk is acceptable. Proceed with caution."

    if alt_route:
        alt_mid = alt_route[len(alt_route) // 2]
        alt_weather = weather_service.get_live_weather(alt_mid.lat, alt_mid.lng)
        alternative = _analyze_route(alt_route, alt_weather, official_warning_level)

        if alternative.overall_score < primary.overall_score:
            recommendation = "Alternative route has lower risk. Recommend switching."
        else:
            recommendation = "Current route is the safer (or equal) option. No change recommended."
    else:
        if primary.overall_level in ("HIGH", "CRITICAL"):
            recommendation = "Route risk is high. Consider requesting an alternative route."

    return primary, alternative, recommendation
