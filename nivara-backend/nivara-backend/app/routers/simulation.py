from fastapi import APIRouter
from app.services import simulation_service
from app.models.schemas import SimulationStepRequest, SimulationStepResponse

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/step", response_model=SimulationStepResponse)
def simulation_step(req: SimulationStepRequest):
    """
    POST /api/simulation/step
    Frontend/Member 5 calls this repeatedly (e.g. every tick of a timer, or
    when the user drags a "elapsed_minutes" slider from 0 to 60) to animate
    the flood scenario. Reuses the exact same risk engine as live mode.
    """
    position, progress_pct, weather, risk = simulation_service.step(
        scenario=req.scenario,
        start=req.start,
        destination=req.destination,
        elapsed_minutes=req.elapsed_minutes,
    )
    return SimulationStepResponse(
        elapsed_minutes=req.elapsed_minutes,
        position=position,
        progress_pct=progress_pct,
        weather=weather,
        risk=risk,
    )
