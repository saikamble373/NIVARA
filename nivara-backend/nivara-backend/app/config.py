"""
Central configuration for NIVARA backend.
Change weights/thresholds here only — every service reads from this file,
so the whole risk model can be tuned in one place without touching logic.
"""

# ---- Risk Engine weights (must sum to 1.0) ----
RISK_WEIGHTS = {
    "rainfall": 0.20,          # current rainfall intensity
    "forecast_rainfall": 0.15, # forecasted rainfall (next few hours)
    "flood_exposure": 0.25,    # is the point inside / near a hazard polygon
    "official_warning": 0.20,  # IMD / govt warning level
    "route_exposure": 0.15,    # % of route passing through hazard zones
    "river_proximity": 0.05,   # distance to nearest river/flood-prone drain
}

assert abs(sum(RISK_WEIGHTS.values()) - 1.0) < 1e-6, "RISK_WEIGHTS must sum to 1.0"

# ---- Risk level thresholds ----
RISK_LEVELS = [
    (0, 30, "LOW"),
    (31, 60, "MODERATE"),
    (61, 80, "HIGH"),
    (81, 100, "CRITICAL"),
]

# ---- Official warning severity → 0-100 score ----
WARNING_LEVEL_SCORES = {
    "none": 0,
    "advisory": 30,
    "watch": 55,
    "warning": 80,
    "severe": 100,
}

# ---- Rainfall intensity bands (mm/hr) — IMD classification, used to normalize ----
# (upper_bound_mm_per_hr, score)
RAINFALL_BANDS = [
    (2.5, 10),      # light
    (7.5, 30),      # moderate
    (35.5, 60),     # heavy
    (124.4, 85),    # very heavy
    (float("inf"), 100),  # extremely heavy
]

# ---- River proximity: distance decay ----
RIVER_PROXIMITY_MAX_KM = 3.0   # beyond this distance, contributes ~0 risk

# ---- CORS: allow all for hackathon; tighten before final demo if needed ----
CORS_ORIGINS = ["*"]

# ---- Fallback mode ----
USE_FALLBACK_WEATHER_ON_FAILURE = True

# ---- Mumbai default center (used for demo / simulation defaults) ----
DEFAULT_CENTER = {"lat": 19.0760, "lng": 72.8777}
