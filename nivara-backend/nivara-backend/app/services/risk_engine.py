"""
NIVARA Risk Engine
------------------
Explainable weighted scoring model. NOT a black-box ML model on purpose
(see roadmap section 20/21: "Do not overbuild the AI").

Every score comes with a `breakdown` showing exactly which factors and
weights produced it, and a plain-English `reason` per factor - this is what
lets Member 6 build the "personalized action" text and what you'll show
during the risk-engine part of the pitch.

This same function is used for BOTH live GPS risk and simulation risk
(roadmap explicitly says: do not build a separate risk engine for simulation).
"""
from datetime import datetime
from app.config import RISK_WEIGHTS, RISK_LEVELS, WARNING_LEVEL_SCORES, RAINFALL_BANDS
from app.models.schemas import RiskBreakdownItem, RiskResponse


def _score_rainfall(mm_per_hr: float) -> float:
    """Map rainfall intensity (mm/hr) to a 0-100 score using IMD-style bands."""
    for upper_bound, score in RAINFALL_BANDS:
        if mm_per_hr <= upper_bound:
            return float(score)
    return 100.0


def _score_warning(level: str) -> float:
    return float(WARNING_LEVEL_SCORES.get((level or "none").lower(), 0))


def _level_for_score(score: float) -> str:
    for low, high, label in RISK_LEVELS:
        if low <= score <= high:
            return label
    return "CRITICAL" if score > 100 else "LOW"


def calculate_risk(
    lat: float,
    lng: float,
    rainfall_mm: float,
    forecast_rainfall_mm: float,
    flood_exposure_score: float,     # 0-100, from hazard_service (point-in-polygon / distance)
    official_warning_level: str,
    route_exposure_pct: float,       # 0-100, from route_service. 0 if not applicable.
    river_proximity_score: float,    # 0-100, from hazard_service
) -> RiskResponse:
    """
    Pure function: given normalized inputs, returns the full explainable RiskResponse.
    Keeping this pure (no I/O) makes it trivially unit-testable and reusable
    from /api/risk, /api/route-risk and /api/simulation alike.
    """
    rainfall_score = _score_rainfall(rainfall_mm)
    forecast_score = _score_rainfall(forecast_rainfall_mm)
    warning_score = _score_warning(official_warning_level)

    raw_values = {
        "rainfall": rainfall_mm,
        "forecast_rainfall": forecast_rainfall_mm,
        "flood_exposure": flood_exposure_score,
        "official_warning": warning_score,
        "route_exposure": route_exposure_pct,
        "river_proximity": river_proximity_score,
    }
    normalized_scores = {
        "rainfall": rainfall_score,
        "forecast_rainfall": forecast_score,
        "flood_exposure": flood_exposure_score,
        "official_warning": warning_score,
        "route_exposure": route_exposure_pct,
        "river_proximity": river_proximity_score,
    }

    reasons = {
        "rainfall": f"Current rainfall is {rainfall_mm:.1f} mm/hr.",
        "forecast_rainfall": f"Rainfall is forecast to reach {forecast_rainfall_mm:.1f} mm/hr soon.",
        "flood_exposure": "Location is inside or very near a known flood-prone zone."
                           if flood_exposure_score >= 60
                           else ("Location is moderately close to a flood-prone zone."
                                 if flood_exposure_score >= 25
                                 else "Location is not near a known flood-prone zone."),
        "official_warning": f"Official warning level: {official_warning_level or 'none'}.",
        "route_exposure": f"{route_exposure_pct:.0f}% of the selected route passes through hazard zones."
                           if route_exposure_pct > 0
                           else "No route selected / route does not cross hazard zones.",
        "river_proximity": "Location is close to a river or major drain."
                            if river_proximity_score >= 50
                            else "Location is not close to a major river/drain.",
    }

    breakdown = []
    total_score = 0.0
    for factor, weight in RISK_WEIGHTS.items():
        norm = normalized_scores[factor]
        contribution = norm * weight
        total_score += contribution
        breakdown.append(RiskBreakdownItem(
            factor=factor,
            weight_pct=round(weight * 100, 1),
            raw_value=round(raw_values[factor], 2),
            normalized_score=round(norm, 1),
            weighted_contribution=round(contribution, 2),
            reason=reasons[factor],
        ))

    total_score = round(min(total_score, 100.0), 1)
    level = _level_for_score(total_score)

    # Build a human summary from the top 2 contributing factors
    top_factors = sorted(breakdown, key=lambda b: b.weighted_contribution, reverse=True)[:2]
    top_reasons = " ".join(f.reason for f in top_factors)
    summary = f"Risk is {level} ({total_score}/100). {top_reasons}"

    return RiskResponse(
        lat=lat,
        lng=lng,
        score=total_score,
        level=level,
        breakdown=breakdown,
        summary=summary,
        calculated_at=datetime.utcnow().isoformat() + "Z",
    )
