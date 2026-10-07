from fastapi import APIRouter
from app.services import route_service
from app.models.schemas import RouteRiskRequest, RouteRiskResponse

router = APIRouter(prefix="/api/route-risk", tags=["route-risk"])


@router.post("", response_model=RouteRiskResponse)
def compute_route_risk(req: RouteRiskRequest):
    """
    POST /api/route-risk
    Send the polyline Member 3's routing service returns (list of {lat,lng}).
    Optionally also send `alt_route` to get a side-by-side comparison and
    a switch/don't-switch recommendation - powers the "safer route" feature.
    """
    primary, alternative, recommendation = route_service.analyze(
        route=req.route,
        alt_route=req.alt_route,
        official_warning_level=req.official_warning_level or "none",
        auto_fetch_weather=req.auto_fetch_weather,
    )
    return RouteRiskResponse(primary=primary, alternative=alternative, recommendation=recommendation)
