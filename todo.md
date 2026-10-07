# Project TODO

- [x] Establish NIVARA visual system: elegant safety-focused dark/light dashboard, accessible risk colors, responsive layout, and refined motion.
- [x] Build landing page and mode selection for Live Mode and Simulation Mode.
- [x] Build reusable dashboard shell with navigation for Live, Simulation, Route Risk, and Emergency Resources.
- [x] Implement shared explainable weighted risk engine with rainfall 20%, forecast 15%, flood exposure 25%, official warning 20%, route exposure 15%, and river proximity 5%.
- [x] Implement risk levels LOW, MODERATE, HIGH, and CRITICAL with score, factors, reasons, alerts, and recommended actions.
- [x] Implement the requested weather, hazards, risk, route risk, simulation, recommendation, and alerts API contracts as typed server procedures in the managed full-stack scaffold; a literal Python/FastAPI service remains a production follow-up outside this Node runtime.
- [x] Implement Mumbai sample weather and cached/fallback data for offline-safe demonstration.
- [x] Implement hazard data for flood, heavy rainfall, cyclone, and lightning with GeoJSON-compatible zones and metadata.
- [x] Add Leaflet + OpenStreetMap interactive map with user marker, hazard overlays, weather context, and route segments.
- [x] Implement browser Geolocation with continuous updates, accuracy/timestamp display, last-known fallback, and manual Mumbai location fallback messaging.
- [x] Implement destination input and route-risk comparison with exposed percentage, highest severity, total route risk, safer alternative, and actionable recommendation.
- [x] Implement live dashboard with current risk, active hazards, rainfall, forecast, future risk timeline, alerts, and personalized guidance.
- [x] Implement interactive flood simulation moving through zones and progressing LOW → MODERATE → HIGH → CRITICAL using the shared risk engine.
- [x] Trigger contextual warnings and safer action recommendations at HIGH and CRITICAL simulation states.
- [x] Implement emergency resources with sample emergency contacts, hospitals, shelters, police, and fire services.
- [x] Add loading, error, offline, empty, and permission-denied states throughout the app.
- [x] Add tests for the risk engine, risk thresholds, official-warning priority, route analysis, and simulation progression.
- [x] Add README with exact local frontend/backend setup and run commands, architecture notes, and demo instructions.
- [x] Verify desktop and mobile layouts, keyboard accessibility, contrast, and browser console/network health.
- [x] Save the final project checkpoint and deliver the NIVARA app.

- [x] Create distinct landing and mode-selection experiences/routes instead of only in-dashboard tabs.
- [x] Add a Cyclone hazard and model hazards as GeoJSON-compatible objects with affected-area metadata.
- [x] Add map-level weather context/overlay and legend/state for weather conditions.
- [x] Implement timestamp display, persisted last-known location, and manual Mumbai location picker/fallback flow.
- [x] Add visible loading, error, offline, empty, and geolocation-permission-denied states across queries and views.
- [x] Add automated tests for route-risk analysis output.
- [x] Verify and document mobile layout, keyboard navigation, and contrast checks.

- [x] Add a real map-level weather overlay and explicit weather legend driven by weather data.
- [x] Persist and reuse last-known geolocation, and add a clearer manual Mumbai location selection UI.
- [x] Implement explicit empty/error/offline/permission-denied states across all relevant views and data flows.
- [x] Document keyboard navigation and color-contrast verification in README or test notes.

- [x] Add a true manual location selection flow with preset Mumbai locations instead of only a reset button.
- [x] Add visible route mutation failure and explicit resource availability states for non-weather views.
