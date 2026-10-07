from fastapi import APIRouter
from app.services import recommendation_service
from app.models.schemas import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/api/recommendation", tags=["recommendation"])


@router.post("", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest):
    """POST /api/recommendation -> turns a risk score/level into concrete next-step actions."""
    return recommendation_service.get_recommendation(
        risk_score=req.risk_score,
        risk_level=req.risk_level,
        route_hazardous=req.route_hazardous,
        has_alt_route=req.has_alt_route,
    )
