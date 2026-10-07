from fastapi import APIRouter
from app.services import alert_service
from app.models.schemas import AlertRequest, AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=AlertResponse)
def get_alert(req: AlertRequest):
    """POST /api/alerts -> decides if this risk update deserves a push alert, and formats it."""
    return alert_service.build_alert(
        location_label=req.location_label,
        risk_score=req.risk_score,
        risk_level=req.risk_level,
        reasons=req.reasons,
    )
