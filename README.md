# NIVARA — Personal Disaster Risk Intelligence

NIVARA is a polished hackathon MVP for understanding personalized flood and severe-weather risk in Mumbai. It connects location context, prototype weather and hazard data, an explainable weighted risk engine, route exposure, and actionable safety guidance in one responsive command-center interface.

## What is implemented

The dashboard includes Live and Simulation modes, a responsive dark safety-console design, interactive Leaflet/OpenStreetMap mapping, hazard zones, dangerous and safer route overlays, current and future risk, contextual alerts, emergency contacts, nearby support locations, and a manual/last-known Mumbai fallback when browser GPS is unavailable.

Live and Simulation use the same shared engine in `shared/nivara.ts`. The weighted model is rainfall 20%, forecast 15%, flood exposure 25%, official warning 20%, route exposure 15%, and river proximity 5%. Scores map to LOW (0–30), MODERATE (31–60), HIGH (61–80), and CRITICAL (81–100). Official-warning guidance takes priority over personalized route optimization.

The current managed web scaffold uses typed server procedures exposed through the app router. The procedure contracts cover weather, hazards, risk, route risk, simulation, recommendations, and alerts. This keeps the demo self-contained and resilient without requiring a live disaster API or external map key. The prototype is intentionally sample-data based and does not claim to predict earthquakes or override official warnings.

## Local development

From the project root, install dependencies and start the managed full-stack development server:

```bash
pnpm install
pnpm dev
```

Run validation and tests:

```bash
pnpm check
pnpm test
```

Build the production bundle:

```bash
pnpm build
pnpm start
```

The Vite client is under `client/`. Server procedures are under `server/`, and reusable weather, hazard, route, simulation, and risk logic is under `shared/nivara.ts`.

## Demo sequence

Open the dashboard and keep Live selected to see the Mumbai fallback location, the high-risk sample state, current heavy rain, active hazard zones, future risk timeline, and the recommended safer-route action. Open **Route risk** to enter a destination and compare the current route with Alternative Route B. Select **Simulate**, then start the scenario to advance the sample position through LOW, MODERATE, HIGH, and CRITICAL states. Open **Emergency resources** for sample emergency contacts and nearby support locations.

## Data and safety notes

Prototype weather, hazards, routes, and emergency resources are sample data intended for demonstration. Browser geolocation is requested only when available; if permission is denied or a browser does not support it, NIVARA clearly communicates that live location is unavailable and continues using the Mumbai fallback. In a production deployment, official alert feeds and verified local resources should replace prototype data. Always follow official emergency and evacuation guidance first.

## Mapping

NIVARA uses Leaflet with OpenStreetMap tiles and does not depend on Google Maps or Google API keys.

## Validation notes

The dashboard was checked at desktop and mobile widths, with keyboard-reachable buttons and form controls, visible focus behavior from the shared component system, and high-contrast risk states against the dark console background. The app also exposes cached, offline, loading, and geolocation-permission messaging rather than failing silently. Last-known coordinates are stored in browser local storage for the next session; the **Use Mumbai** control provides a clear manual fallback.
