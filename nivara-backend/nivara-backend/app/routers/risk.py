from fastapi import APIRouter
from app.services import weather_service, hazard_service, risk_engine
from app.models.schemas import RiskRequest, RiskResponse

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("", response_model=RiskResponse)
def compute_risk(req: RiskRequest):
    """
    POST /api/risk
    The core endpoint. Give it a lat/lng (and optionally raw weather values),
    it returns a full explainable risk score + breakdown.
    If rainfall values aren't supplied, it auto-fetches live weather.
    """
    if req.rainfall_mm is not None and req.forecast_rainfall_mm is not None:
        rainfall_mm = req.rainfall_mm
        forecast_rainfall_mm = req.forecast_rainfall_mm
    else:
        weather = weather_service.get_live_weather(req.lat, req.lng)
        rainfall_mm = weather.rainfall_mm
        forecast_rainfall_mm = weather.forecast_rainfall_mm

    if req.auto_check_hazards:
        flood_exposure_score, _ = hazard_service.flood_exposure_for_point(req.lat, req.lng)
        river_score = hazard_service.river_proximity_for_point(req.lat, req.lng)
    else:
        flood_exposure_score, river_score = 0.0, 0.0

    return risk_engine.calculate_risk(
        lat=req.lat,
        lng=req.lng,
        rainfall_mm=rainfall_mm,
        forecast_rainfall_mm=forecast_rainfall_mm,
        flood_exposure_score=flood_exposure_score,
        official_warning_level=req.official_warning_level or "none",
        route_exposure_pct=req.route_exposure_pct or 0.0,
        river_proximity_score=river_score,
    )
