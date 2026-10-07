"""
Simulation service.

Roadmap requirement (section 10 / demo section 15): a scripted flood
scenario where simulated risk climbs LOW -> MODERATE -> HIGH -> CRITICAL
over ~60 simulated minutes as the user moves toward a hazard zone.

Critically, this does NOT use a separate risk model - it generates
plausible weather inputs for a given elapsed time, then calls the exact
same risk_engine.calculate_risk() used by live GPS mode. That's what the
roadmap means by "Connect simulated GPS to the same risk engine used by
live GPS."

Member 5 owns tuning `_scripted_rainfall_curve` for the actual demo scenario.
"""
from datetime import datetime
from app.models.schemas import Coordinates, WeatherResponse, HourlyForecast
from app.services import hazard_service, risk_engine

TOTAL_DEMO_MINUTES = 60  # matches roadmap demo: 00:00 -> 01:00


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _interpolate_position(start: Coordinates, destination: Coordinates, progress: float) -> Coordinates:
    progress = max(0.0, min(1.0, progress))
    return Coordinates(
        lat=_lerp(start.lat, destination.lat, progress),
        lng=_lerp(start.lng, destination.lng, progress),
    )


def _scripted_rainfall_curve(elapsed_minutes: float):
    """
    Produces (rainfall_mm, forecast_rainfall_mm) that climbs over time so the
    demo reliably shows LOW -> MODERATE -> HIGH -> CRITICAL by minute 60.
    """
    t = max(0.0, min(1.0, elapsed_minutes / TOTAL_DEMO_MINUTES))
    rainfall = _lerp(3.0, 140.0, t)      # light drizzle -> extremely heavy
    forecast = _lerp(8.0, 160.0, t)
    return round(rainfall, 1), round(forecast, 1)


def step(scenario: str, start: Coordinates, destination: Coordinates, elapsed_minutes: float):
    progress = elapsed_minutes / TOTAL_DEMO_MINUTES
    position = _interpolate_position(start, destination, progress)

    rainfall_mm, forecast_rainfall_mm = _scripted_rainfall_curve(elapsed_minutes)

    weather = WeatherResponse(
        lat=position.lat,
        lng=position.lng,
        rainfall_mm=rainfall_mm,
        forecast_rainfall_mm=forecast_rainfall_mm,
        temperature_c=27.0,
        wind_kmph=12.0,
        precipitation_probability=min(95.0, 40 + progress * 55),
        hourly=[
            HourlyForecast(time="+1h", rainfall_mm=forecast_rainfall_mm, temperature_c=26.5,
                            precipitation_probability=min(95.0, 40 + progress * 55)),
        ],
        source="simulation",
        fetched_at=datetime.utcnow().isoformat() + "Z",
    )

    flood_exposure_score, _ = hazard_service.flood_exposure_for_point(position.lat, position.lng)
    river_score = hazard_service.river_proximity_for_point(position.lat, position.lng)

    # As the scenario progresses, escalate the "official warning" too -
    # mirrors how real warnings get upgraded as a storm develops.
    if progress < 0.25:
        warning_level = "none"
    elif progress < 0.5:
        warning_level = "advisory"
    elif progress < 0.75:
        warning_level = "watch"
    elif progress < 0.9:
        warning_level = "warning"
    else:
        warning_level = "severe"

    risk = risk_engine.calculate_risk(
        lat=position.lat,
        lng=position.lng,
        rainfall_mm=rainfall_mm,
        forecast_rainfall_mm=forecast_rainfall_mm,
        flood_exposure_score=flood_exposure_score,
        official_warning_level=warning_level,
        route_exposure_pct=0.0,
        river_proximity_score=river_score,
    )

    return position, round(progress * 100, 1), weather, risk
