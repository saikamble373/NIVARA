/**
 * Client for Member 4's NIVARA FastAPI backend.
 *
 * Field names here are copied 1:1 from nivara-backend/app/models/schemas.py,
 * which the backend README calls "the single source of truth". Do not rename
 * fields on this side — if the contract changes, change it there first, then
 * mirror the change here.
 *
 * Base URL comes from ENV.riskEngineUrl (env var RISK_ENGINE_URL), defaulting
 * to http://localhost:8000 for local dev alongside `uvicorn main:app`.
 */
import { ENV } from "./_core/env";

const BASE_URL = ENV.riskEngineUrl.replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`NIVARA backend ${path} -> ${res.status}: ${body || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// ---------- shared ----------

export interface Coordinates {
  lat: number;
  lng: number;
}

// ---------- weather ----------

export interface HourlyForecast {
  time: string;
  rainfall_mm: number;
  temperature_c: number;
  precipitation_probability: number;
}

export interface WeatherResponse {
  lat: number;
  lng: number;
  rainfall_mm: number;
  forecast_rainfall_mm: number;
  temperature_c: number;
  wind_kmph: number;
  precipitation_probability: number;
  hourly: HourlyForecast[];
  source: "live" | "fallback" | "simulation";
  fetched_at: string;
}

export function getWeather(lat: number, lng: number): Promise<WeatherResponse> {
  return request(`/api/weather?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}`);
}

// ---------- hazards ----------

export interface HazardZone {
  centroid: Coordinates;
  radius_km: number;
  risk_score: number;
  id: string;
  name: string;
  hazard_type: string;
  severity: "low" | "moderate" | "high" | string;
  geometry: Record<string, unknown>;
}

export interface HazardResponse {
  zones: HazardZone[];
  source: string;
}

export function getHazards(): Promise<HazardResponse> {
  return request(`/api/hazards`);
}

// ---------- risk engine ----------

export interface RiskRequest {
  lat: number;
  lng: number;
  rainfall_mm?: number;
  forecast_rainfall_mm?: number;
  official_warning_level?: string;
  route_exposure_pct?: number;
  auto_fetch_weather?: boolean;
  auto_check_hazards?: boolean;
}

export interface RiskBreakdownItem {
  factor: string;
  weight_pct: number;
  raw_value: number;
  normalized_score: number;
  weighted_contribution: number;
  reason: string;
}

export interface RiskResponse {
  lat: number;
  lng: number;
  score: number;
  level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  breakdown: RiskBreakdownItem[];
  summary: string;
  calculated_at: string;
}

export function postRisk(req: RiskRequest): Promise<RiskResponse> {
  return request(`/api/risk`, { method: "POST", body: JSON.stringify(req) });
}

// ---------- route risk ----------

export interface RouteRiskRequest {
  route: Coordinates[];
  alt_route?: Coordinates[];
  official_warning_level?: string;
  auto_fetch_weather?: boolean;
}

export interface RouteSegmentRisk {
  segment_index: number;
  start: Coordinates;
  end: Coordinates;
  in_hazard_zone: boolean;
  hazard_names: string[];
}

export interface RouteRiskResult {
  overall_score: number;
  overall_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  route_exposure_pct: number;
  segments: RouteSegmentRisk[];
  hazardous_segment_count: number;
}

export interface RouteRiskResponse {
  primary: RouteRiskResult;
  alternative?: RouteRiskResult;
  recommendation: string;
}

export function postRouteRisk(req: RouteRiskRequest): Promise<RouteRiskResponse> {
  return request(`/api/route-risk`, { method: "POST", body: JSON.stringify(req) });
}

// ---------- simulation ----------

export interface SimulationStepRequest {
  scenario?: string;
  start: Coordinates;
  destination: Coordinates;
  elapsed_minutes: number;
}

export interface SimulationStepResponse {
  elapsed_minutes: number;
  position: Coordinates;
  progress_pct: number;
  weather: WeatherResponse;
  risk: RiskResponse;
}

export function postSimulationStep(req: SimulationStepRequest): Promise<SimulationStepResponse> {
  return request(`/api/simulation/step`, { method: "POST", body: JSON.stringify(req) });
}

// ---------- recommendation ----------

export interface RecommendationRequest {
  risk_score: number;
  risk_level: string;
  route_hazardous?: boolean;
  has_alt_route?: boolean;
}

export interface RecommendationResponse {
  primary_action: string;
  actions: string[];
  message: string;
}

export function postRecommendation(req: RecommendationRequest): Promise<RecommendationResponse> {
  return request(`/api/recommendation`, { method: "POST", body: JSON.stringify(req) });
}

// ---------- alerts ----------

export interface AlertRequest {
  location_label?: string;
  risk_score: number;
  risk_level: string;
  reasons?: string[];
}

export interface AlertResponse {
  should_alert: boolean;
  severity: string;
  alert_message: string;
}

export function postAlert(req: AlertRequest): Promise<AlertResponse> {
  return request(`/api/alerts`, { method: "POST", body: JSON.stringify(req) });
}
