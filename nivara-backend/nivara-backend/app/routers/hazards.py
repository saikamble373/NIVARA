from fastapi import APIRouter
from app.services import hazard_service
from app.models.schemas import HazardResponse

router = APIRouter(prefix="/api/hazards", tags=["hazards"])


@router.get("", response_model=HazardResponse)
def get_hazards():
    """GET /api/hazards -> all known hazard zones (GeoJSON), for Member 3 to draw on the map."""
    zones = hazard_service.get_all_zones()
    return HazardResponse(zones=zones, source="mumbai_hazard_zones.geojson")
