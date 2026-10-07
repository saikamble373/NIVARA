import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { ALERT_COPY, conditionFromRainfall, MUMBAI_CENTER, ROUTES } from "@shared/nivara";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import * as nivara from "./nivaraClient";
import type { RiskResponse, WeatherResponse } from "./nivaraClient";

const coordsSchema = z.object({ lat: z.number(), lng: z.number() });

// Demo simulation path: from Mumbai center toward the Bandra Kurla Complex
// hazard zone, matching the original scripted scenario's endpoint.
const SIMULATION_START = MUMBAI_CENTER;
const SIMULATION_DESTINATION = { lat: 19.061, lng: 72.864 };
const SIMULATION_STEP_MINUTES = [0, 20, 40, 60]; // maps step 0-3 -> elapsed_minutes

/**
 * Turns the backend's RiskResponse (score/level/breakdown/summary) plus a
 * RecommendationResponse into the shape the dashboard UI already expects
 * (score/level/reasons/alert/recommendation), so Home.tsx keeps working
 * without needing to know about `breakdown` items directly.
 */
async function toDashboardRisk(risk: RiskResponse) {
  const recommendation = await nivara.postRecommendation({
    risk_score: risk.score,
    risk_level: risk.level,
    route_hazardous: false,
    has_alt_route: false,
  });

  const reasons = [...risk.breakdown]
    .sort((a, b) => b.weighted_contribution - a.weighted_contribution)
    .filter((b) => b.weighted_contribution > 0)
    .slice(0, 4)
    .map((b) => b.reason);

  return {
    score: risk.score,
    level: risk.level,
    breakdown: risk.breakdown,
    reasons,
    alert: ALERT_COPY[risk.level],
    recommendation: recommendation.message,
    summary: risk.summary,
    calculatedAt: risk.calculated_at,
  };
}

function toDashboardWeather(w: WeatherResponse) {
  return {
    location: "Mumbai, Maharashtra",
    temperature: w.temperature_c,
    condition: conditionFromRainfall(w.rainfall_mm),
    rainfall: w.rainfall_mm,
    forecastRainfall: w.forecast_rainfall_mm,
    wind: w.wind_kmph,
    precipitationProbability: w.precipitation_probability,
    updatedAt: w.fetched_at,
    source: w.source,
    forecast: w.hourly.map((h) => ({
      time: h.time,
      label: conditionFromRainfall(h.rainfall_mm),
      value: h.precipitation_probability,
      temp: h.temperature_c,
    })),
  };
}

function toDashboardHazards(zones: nivara.HazardZone[]) {
  return zones.map((z) => ({
    id: z.id,
    type: z.hazard_type.charAt(0).toUpperCase() + z.hazard_type.slice(1),
    severity: z.severity.toUpperCase(),
    riskScore: z.risk_score,
    status: z.risk_score >= 70 ? "Active" : "Monitoring",
    description: `${z.severity[0].toUpperCase()}${z.severity.slice(1)} ${z.hazard_type} risk zone: ${z.name}.`,
    timestamp: new Date().toISOString(),
    center: [z.centroid.lat, z.centroid.lng] as [number, number],
    radius: z.radius_km / 111, // km -> degrees, to match the Leaflet Circle radius math in MapPanel
    affectedArea: z.name,
    geometry: z.geometry,
  }));
}

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // GET /api/weather?lat&lng on the FastAPI backend
  weather: publicProcedure.input(coordsSchema.optional()).query(async ({ input }) => {
    const { lat, lng } = input ?? MUMBAI_CENTER;
    const w = await nivara.getWeather(lat, lng);
    return toDashboardWeather(w);
  }),

  // GET /api/hazards on the FastAPI backend
  hazards: publicProcedure.query(async () => {
    const res = await nivara.getHazards();
    return { hazards: toDashboardHazards(res.zones), center: MUMBAI_CENTER, source: res.source };
  }),

  // POST /api/risk (+ /api/recommendation) on the FastAPI backend — this is
  // the real, live-GPS risk score. Replaces the old client-side calculateRisk
  // stub that used hardcoded factor numbers.
  risk: publicProcedure.input(coordsSchema.optional()).query(async ({ input }) => {
    const { lat, lng } = input ?? MUMBAI_CENTER;
    const risk = await nivara.postRisk({ lat, lng, official_warning_level: "none" });
    return toDashboardRisk(risk);
  }),

  // POST /api/route-risk on the FastAPI backend. Duration/distance still
  // come from the sample ROUTES polylines (no real routing/directions
  // provider is wired up yet) — but the risk scoring itself is real,
  // computed against the actual hazard zones and live weather.
  routeRisk: publicProcedure
    .input(z.object({ destination: z.string().optional() }))
    .mutation(async ({ input }) => {
      const toCoords = (pts: [number, number][]) => pts.map(([lat, lng]) => ({ lat, lng }));
      const result = await nivara.postRouteRisk({
        route: toCoords(ROUTES.current.coordinates),
        alt_route: toCoords(ROUTES.alternative.coordinates),
        official_warning_level: "none",
      });

      const build = (base: typeof ROUTES.current, r: nivara.RouteRiskResult) => ({
        ...base,
        risk: r.overall_score,
        severity: r.overall_level,
        exposed: r.route_exposure_pct,
      });

      return {
        current: build(ROUTES.current, result.primary),
        alternative: result.alternative ? build(ROUTES.alternative, result.alternative) : ROUTES.alternative,
        destination: input.destination || "Bandra Kurla Complex",
        recommendation: result.recommendation,
      };
    }),

  // POST /api/simulation/step on the FastAPI backend — same risk engine as
  // live mode, walking a scripted path toward a hazard zone.
  simulation: publicProcedure
    .input(z.object({ step: z.number().int().min(0).max(3) }))
    .query(async ({ input }) => {
      const elapsed_minutes = SIMULATION_STEP_MINUTES[input.step];
      const stepResult = await nivara.postSimulationStep({
        scenario: "mumbai_flood",
        start: SIMULATION_START,
        destination: SIMULATION_DESTINATION,
        elapsed_minutes,
      });
      const risk = await toDashboardRisk(stepResult.risk);
      return {
        step: input.step,
        location: [stepResult.position.lat, stepResult.position.lng] as [number, number],
        progressPct: stepResult.progress_pct,
        weather: toDashboardWeather(stepResult.weather),
        risk,
      };
    }),

  // POST /api/recommendation on the FastAPI backend, exposed directly too
  // (per README: used by Member 6 for action-engine text).
  recommendation: publicProcedure
    .input(
      z.object({
        riskScore: z.number(),
        riskLevel: z.enum(["LOW", "MODERATE", "HIGH", "CRITICAL"]),
        routeHazardous: z.boolean().default(false),
        hasAltRoute: z.boolean().default(false),
      }),
    )
    .mutation(({ input }) =>
      nivara.postRecommendation({
        risk_score: input.riskScore,
        risk_level: input.riskLevel,
        route_hazardous: input.routeHazardous,
        has_alt_route: input.hasAltRoute,
      }),
    ),

  // POST /api/alerts on the FastAPI backend.
  alerts: publicProcedure
    .input(
      z.object({
        locationLabel: z.string().default("Current Location"),
        riskScore: z.number(),
        riskLevel: z.string(),
        reasons: z.array(z.string()).default([]),
      }),
    )
    .mutation(({ input }) =>
      nivara.postAlert({
        location_label: input.locationLabel,
        risk_score: input.riskScore,
        risk_level: input.riskLevel,
        reasons: input.reasons,
      }),
    ),
});

export type AppRouter = typeof appRouter;
