# NIVARA Backend — Member 4 (Backend + Risk Engine)

FastAPI backend implementing the risk engine and all API endpoints from the
roadmap. Tested end-to-end and working. This is the contract the whole team
builds against — send this file (or just the repo) to everyone.

## Quick start

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000/docs** — interactive Swagger UI, auto-generated
from the code. Send this link in your team group; everyone can test requests
straight from the browser without writing any code first.

## Project structure

```
nivara-backend/
├── main.py                        # FastAPI app, CORS, router registration
├── requirements.txt
├── app/
│   ├── config.py                  # risk weights, thresholds — tune the model here
│   ├── models/schemas.py          # THE API CONTRACT (request/response shapes)
│   ├── services/
│   │   ├── risk_engine.py         # core explainable weighted scoring (pure function)
│   │   ├── weather_service.py     # live weather (Open-Meteo, no key needed) + fallback
│   │   ├── hazard_service.py      # point-in-polygon / proximity checks (shapely)
│   │   ├── route_service.py       # route-risk analysis, primary vs alt route
│   │   ├── simulation_service.py  # reuses risk_engine for the demo scenario
│   │   ├── recommendation_service.py
│   │   └── alert_service.py
│   ├── routers/                   # one file per endpoint group
│   └── data/
│       ├── mumbai_hazard_zones.geojson   # sample hazard polygons (Hindmata, Kurla, Sion, Andheri)
│       └── fallback_weather.json         # used automatically if live weather API fails
```

## Why it's structured this way (so it's easy to integrate)

- **`app/models/schemas.py` is the single source of truth.** Every field name
  in every request/response is defined there. If frontend/maps/weather people
  ask "what does the API expect", point them at this file or at `/docs`.
- **`risk_engine.calculate_risk()` is a pure function** — no I/O, same
  function used by live GPS risk, route risk, and simulation. This is exactly
  what the roadmap means by "don't build a separate risk engine for
  simulation" (Hours 24–30).
- **Fallback data is built in.** If the weather API is unreachable during the
  actual demo (bad wifi at the venue), `/api/weather` silently returns
  `app/data/fallback_weather.json` instead of crashing. `source` field tells
  you which one you got (`"live"` / `"fallback"` / `"simulation"`).
- **Hazard zones are just a GeoJSON file.** Member 5 can replace
  `app/data/mumbai_hazard_zones.geojson` with better/more zones — same
  schema, nothing else needs to change.

## API Contract — what to send, what you get back

### `GET /api/weather?lat=..&lng=..`
Returns current + forecast rainfall, temp, wind for a point.
Used by: dashboard weather card (Member 2), risk engine (internal).

### `GET /api/hazards`
Returns all hazard zones as GeoJSON polygons — feed this straight into a
Leaflet `L.geoJSON()` layer.
Used by: Member 3 (map).

### `POST /api/risk`
```json
{ "lat": 19.002, "lng": 72.838, "official_warning_level": "warning" }
```
Returns `score` (0–100), `level` (LOW/MODERATE/HIGH/CRITICAL), and a
`breakdown` array — one entry per weighted factor with its own plain-English
`reason`. This is what you show on stage to prove the AI isn't a black box.
If you don't send `rainfall_mm`/`forecast_rainfall_mm`, it auto-fetches
weather for you.
Used by: dashboard risk card (Member 2), Member 6 for action text.

### `POST /api/route-risk`
```json
{
  "route": [{"lat":.., "lng":..}, ...],
  "alt_route": [{"lat":.., "lng":..}, ...],
  "official_warning_level": "warning"
}
```
`route`/`alt_route` are polylines from Member 3's routing service. Returns
risk for each, plus `recommendation` telling you whether to switch.
Used by: route analysis page (Member 2/3).

### `POST /api/simulation/step`
```json
{ "start": {"lat":19.20,"lng":72.97}, "destination": {"lat":19.002,"lng":72.838}, "elapsed_minutes": 30 }
```
Call this repeatedly (e.g. a slider or timer from 0→60 "minutes") to animate
the flood scenario. Returns the interpolated position, weather at that
moment, and risk — using the exact same risk engine as live mode. Tested to
progress LOW → MODERATE → HIGH → CRITICAL by minute 60.
Used by: simulation page (Member 2/5).

### `POST /api/recommendation`
```json
{ "risk_score": 85, "risk_level": "CRITICAL", "route_hazardous": true, "has_alt_route": true }
```
Returns `primary_action` + a list of concrete `actions` for the UI.
Used by: Member 6 (action engine UI).

### `POST /api/alerts`
```json
{ "location_label": "College Route", "risk_score": 67, "risk_level": "HIGH", "reasons": ["..."] }
```
Returns whether this update deserves a push alert and a formatted message.
Used by: Member 6 (alert/toast component).

## Tested and confirmed working (22 Aug)

- All 7 routes registered and respond correctly.
- `/api/risk` correctly scores LOW away from hazard zones, HIGH/CRITICAL
  inside them, with full explainable breakdown.
- `/api/route-risk` correctly flags a hazardous route as HIGH and an
  alternative as lower risk, with a switch recommendation.
- `/api/simulation/step` confirmed to progress LOW → MODERATE → CRITICAL
  over 0–60 simulated minutes, reusing the same risk engine.
- Weather fallback confirmed working when the live API is unreachable.

## Integration checklist for each member

- **Member 2 (Frontend)**: point axios/fetch calls at these routes. CORS is
  already open (`allow_origins=["*"]`) so localhost dev will just work.
- **Member 3 (Maps)**: use `/api/hazards` for polygons, send your route
  polyline to `/api/route-risk`.
- **Member 5 (Weather/Sim)**: swap `app/data/mumbai_hazard_zones.geojson` for
  a better one if you build it; tune `simulation_service._scripted_rainfall_curve()`
  if you want a different escalation pace for the demo.
- **Member 6 (Action/QA)**: `/api/recommendation` and `/api/alerts` give you
  ready-made text — no need to hardcode messages in the frontend.
- **Member 1 (Lead)**: deploy this as-is (`uvicorn main:app`), or containerize
  — no external DB required for the 48-hour prototype (in-memory + file data only).
