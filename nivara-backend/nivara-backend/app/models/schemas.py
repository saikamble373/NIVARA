"""
Pydantic request/response models.
This file IS the API contract - Members 2 (frontend), 3 (maps), 5 (weather/sim)
should treat these field names as fixed. FastAPI auto-generates /docs from these.
"""
from pydantic import BaseModel
from typing import List, Optional


# ---------- shared ----------

class Coordinates(BaseModel):
    lat: float
    lng: float


# ---------- weather ----------

class HourlyForecast(BaseModel):
    time: str                      # ISO timestamp
    rainfall_mm: float
    temperature_c: float
    precipitation_probability: float  # 0-100


class WeatherResponse(BaseModel):
    lat: float
    lng: float
    rainfall_mm: float              # current rainfall intensity (mm/hr)
    forecast_rainfall_mm: float     # expected rainfall in next ~3hrs (mm/hr)
    temperature_c: float
    wind_kmph: float
    precipitation_probability: float
    hourly: List[HourlyForecast] = []
    source: str                     # "live" | "fallback" | "simulation"
    fetched_at: str


# ---------- hazards ----------

class HazardZone(BaseModel):
    id: str
    name: str
    hazard_type: str                # "flood" | "waterlogging" | "landslide" etc.
    severity: str                   # "low" | "moderate" | "high"
    geometry: dict                  # raw GeoJSON Polygon/MultiPolygon


class HazardResponse(BaseModel):
    zones: List[HazardZone]
    source: str


# ---------- risk engine ----------

class RiskRequest(BaseModel):
    lat: float
    lng: float
    rainfall_mm: Optional[float] = None
    forecast_rainfall_mm: Optional[float] = None
    official_warning_level: Optional[str] = "none"   # none/advisory/watch/warning/severe
    route_exposure_pct: Optional[float] = None        # 0-100, filled by /api/route-risk internally
    auto_fetch_weather: bool = True
    auto_check_hazards: bool = True


class RiskBreakdownItem(BaseModel):
    factor: str
    weight_pct: float
    raw_value: float
    normalized_score: float   # 0-100
    weighted_contribution: float
    reason: str


class RiskResponse(BaseModel):
    lat: float
    lng: float
    score: float               # 0-100
    level: str                 # LOW/MODERATE/HIGH/CRITICAL
    breakdown: List[RiskBreakdownItem]
    summary: str
    calculated_at: str


# ---------- route risk ----------

class RouteRiskRequest(BaseModel):
    route: List[Coordinates]                # ordered polyline points, from Member 3 (routing)
    alt_route: Optional[List[Coordinates]] = None   # optional 2nd route to compare
    official_warning_level: Optional[str] = "none"
    auto_fetch_weather: bool = True


class RouteSegmentRisk(BaseModel):
    segment_index: int
    start: Coordinates
    end: Coordinates
    in_hazard_zone: bool
    hazard_names: List[str] = []


class RouteRiskResult(BaseModel):
    overall_score: float
    overall_level: str
    route_exposure_pct: float       # % of points inside hazard zones
    segments: List[RouteSegmentRisk]
    hazardous_segment_count: int


class RouteRiskResponse(BaseModel):
    primary: RouteRiskResult
    alternative: Optional[RouteRiskResult] = None
    recommendation: str


# ---------- simulation ----------

class SimulationStartRequest(BaseModel):
    scenario: str = "mumbai_flood"
    start: Coordinates
    destination: Coordinates
    speed_multiplier: float = 1.0


class SimulationStepRequest(BaseModel):
    scenario: str = "mumbai_flood"
    start: Coordinates
    destination: Coordinates
    elapsed_minutes: float          # simulated time elapsed since scenario start


class SimulationStepResponse(BaseModel):
    elapsed_minutes: float
    position: Coordinates
    progress_pct: float
    weather: WeatherResponse
    risk: RiskResponse


# ---------- recommendation ----------

class RecommendationRequest(BaseModel):
    risk_score: float
    risk_level: str
    route_hazardous: bool = False
    has_alt_route: bool = False


class RecommendationResponse(BaseModel):
    primary_action: str
    actions: List[str]
    message: str


# ---------- alerts ----------

class AlertRequest(BaseModel):
    location_label: str = "Current Location"
    risk_score: float
    risk_level: str
    reasons: List[str] = []


class AlertResponse(BaseModel):
    should_alert: bool
    severity: str
    alert_message: str
