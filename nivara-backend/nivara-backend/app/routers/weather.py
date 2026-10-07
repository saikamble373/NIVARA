from fastapi import APIRouter
from app.services import weather_service
from app.models.schemas import WeatherResponse

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("", response_model=WeatherResponse)
def get_weather(lat: float, lng: float):
    """GET /api/weather?lat=..&lng=.. -> live weather, or fallback if the API is down."""
    return weather_service.get_live_weather(lat, lng)
