export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";

export type RiskFactors = {
  rainfall: number;
  forecast: number;
  floodExposure: number;
  officialWarning: number;
  routeExposure: number;
  riverProximity: number;
};

export const RISK_WEIGHTS = {
  rainfall: 0.2,
  forecast: 0.15,
  floodExposure: 0.25,
  officialWarning: 0.2,
  routeExposure: 0.15,
  riverProximity: 0.05,
} as const;

export const MUMBAI_CENTER = { lat: 19.076, lng: 72.8777 };

// Plain-English copy for each risk level, keyed by the backend's `level`
// field (LOW/MODERATE/HIGH/CRITICAL). This is presentation text only — the
// score/level themselves always come from the real risk engine now.
export const ALERT_COPY: Record<RiskLevel, string> = {
  LOW: "Conditions are currently safe. Continue monitoring.",
  MODERATE: "Moderate hazard nearby. Stay alert.",
  HIGH: "High risk detected near your location. Consider avoiding the affected area.",
  CRITICAL: "Critical risk detected. Avoid the affected area and follow official emergency guidance.",
};

// Rough IMD-style rainfall bands, mirrored from the backend's RAINFALL_BANDS
// in app/config.py, used only to derive a human-readable "condition" label
// (the backend itself doesn't return one).
export function conditionFromRainfall(mmPerHr: number): string {
  if (mmPerHr <= 2.5) return "Light rain";
  if (mmPerHr <= 7.5) return "Moderate rain";
  if (mmPerHr <= 35.5) return "Heavy rain";
  if (mmPerHr <= 124.4) return "Very heavy rain";
  return "Extremely heavy rain";
}

// ---------------------------------------------------------------------------
// Everything below is FALLBACK / OFFLINE DEMO DATA ONLY. It is served when
// the live FastAPI backend (Member 4) is unreachable — see routers.ts, which
// tries the real backend first and only falls back to these constants on
// error. Do not treat this as live logic.
// ---------------------------------------------------------------------------

export const SAMPLE_WEATHER = {
  location: "Mumbai, Maharashtra",
  temperature: 27,
  condition: "Heavy rain",
  rainfall: 82,
  forecastRainfall: 94,
  wind: 24,
  precipitationProbability: 91,
  updatedAt: "2026-08-22T08:00:00.000Z",
  source: "fallback" as const,
  forecast: [
    { time: "Now", label: "Heavy rain", value: 82, temp: 27 },
    { time: "+1h", label: "Intensifying", value: 88, temp: 26 },
    { time: "+2h", label: "Peak rainfall", value: 94, temp: 25 },
    { time: "+3h", label: "Easing", value: 76, temp: 26 },
  ],
};

export const HAZARDS = [
  {
    id: "flood-bandra",
    type: "Flood",
    severity: "HIGH",
    riskScore: 85,
    status: "Active",
    description: "Waterlogging reported across low-lying arterial roads near Bandra Kurla Complex.",
    timestamp: "2026-08-22T07:52:00.000Z",
    center: [19.067, 72.868] as [number, number],
    radius: 0.018,
    affectedArea: "Bandra Kurla Complex lowlands",
    geometry: { type: "Point", coordinates: [72.868, 19.067] },
  },
  {
    id: "flood-dadar",
    type: "Flood",
    severity: "MODERATE",
    riskScore: 58,
    status: "Monitoring",
    description: "Drainage capacity reduced around Dadar West following sustained rainfall.",
    timestamp: "2026-08-22T07:31:00.000Z",
    center: [19.018, 72.842] as [number, number],
    radius: 0.014,
    affectedArea: "Dadar West drainage corridor",
    geometry: { type: "Point", coordinates: [72.842, 19.018] },
  },
  {
    id: "rain-south-mumbai",
    type: "Heavy Rainfall",
    severity: "HIGH",
    riskScore: 72,
    status: "Active",
    description: "Very heavy rainfall band moving northeast across the city.",
    timestamp: "2026-08-22T07:45:00.000Z",
    center: [18.96, 72.83] as [number, number],
    radius: 0.028,
    affectedArea: "South Mumbai rainfall band",
    geometry: { type: "Point", coordinates: [72.83, 18.96] },
  },
  {
    id: "lightning-thane",
    type: "Lightning",
    severity: "MODERATE",
    riskScore: 46,
    status: "Monitoring",
    description: "Scattered lightning cells detected north-east of the city.",
    timestamp: "2026-08-22T07:20:00.000Z",
    center: [19.18, 72.97] as [number, number],
    radius: 0.02,
    affectedArea: "Thane Creek corridor",
    geometry: { type: "Point", coordinates: [72.97, 19.18] },
  },
  {
    id: "cyclone-arabian-sea",
    type: "Cyclone",
    severity: "MODERATE",
    riskScore: 44,
    status: "Monitoring",
    description: "Remnant circulation over the Arabian Sea may reinforce rainfall bands along the coast.",
    timestamp: "2026-08-22T06:40:00.000Z",
    center: [18.91, 72.81] as [number, number],
    radius: 0.025,
    affectedArea: "Mumbai coastline",
    geometry: { type: "Point", coordinates: [72.81, 18.91] },
  },
];

export const ROUTES = {
  current: {
    name: "Current route",
    duration: "12 min",
    distance: "4.8 km",
    risk: 78,
    exposed: 42,
    severity: "HIGH" as RiskLevel,
    coordinates: [[19.076, 72.8777], [19.069, 72.872], [19.067, 72.868], [19.059, 72.862], [19.052, 72.857]] as [number, number][],
  },
  alternative: {
    name: "Alternative Route B",
    duration: "15 min",
    distance: "5.6 km",
    risk: 24,
    exposed: 8,
    severity: "LOW" as RiskLevel,
    coordinates: [[19.076, 72.8777], [19.083, 72.884], [19.081, 72.895], [19.069, 72.899], [19.058, 72.89]] as [number, number][],
  },
};

export function getRiskLevel(score: number): RiskLevel {
  if (score <= 30) return "LOW";
  if (score <= 60) return "MODERATE";
  if (score <= 80) return "HIGH";
  return "CRITICAL";
}

export function calculateRisk(factors: RiskFactors) {
  const score = Math.round(
    factors.rainfall * RISK_WEIGHTS.rainfall +
      factors.forecast * RISK_WEIGHTS.forecast +
      factors.floodExposure * RISK_WEIGHTS.floodExposure +
      factors.officialWarning * RISK_WEIGHTS.officialWarning +
      factors.routeExposure * RISK_WEIGHTS.routeExposure +
      factors.riverProximity * RISK_WEIGHTS.riverProximity,
  );
  const level = getRiskLevel(score);
  const reasons: string[] = [];
  if (factors.rainfall >= 70) reasons.push("Heavy rainfall is affecting the area");
  if (factors.forecast >= 70) reasons.push("Rainfall is expected to intensify");
  if (factors.floodExposure >= 60) reasons.push("High flood exposure near your location");
  if (factors.officialWarning >= 60) reasons.push("Official warning is active");
  if (factors.routeExposure >= 60) reasons.push("Your route enters an affected zone");
  if (factors.riverProximity >= 60) reasons.push("You are close to a river or drainage corridor");
  const alert = {
    LOW: "Conditions are currently safe. Continue monitoring.",
    MODERATE: "Moderate hazard nearby. Stay alert.",
    HIGH: "High risk detected near your location. Consider avoiding the affected area.",
    CRITICAL: "Critical risk detected. Avoid the affected area and follow official emergency guidance.",
  }[level];
  const recommendation = factors.officialWarning >= 60 ? (level === "CRITICAL" ? "Avoid the affected area now and follow official emergency guidance." : "Follow official emergency guidance first, monitor updates, and limit unnecessary travel.") : level === "CRITICAL" ? "Avoid the affected area now and follow official emergency guidance." : level === "HIGH" ? "Avoid low-lying areas and use the recommended alternate route." : level === "MODERATE" ? "Stay alert, monitor official updates, and postpone non-essential travel." : "Continue monitoring conditions and keep emergency contacts accessible.";
  return { score, level, factors, reasons, alert, recommendation };
}

export function getSimulationStep(step: number) {
  const scenarios = [
    { location: [19.076, 72.8777] as [number, number], factors: { rainfall: 30, forecast: 36, floodExposure: 18, officialWarning: 20, routeExposure: 12, riverProximity: 20 } },
    { location: [19.069, 72.872] as [number, number], factors: { rainfall: 58, forecast: 64, floodExposure: 46, officialWarning: 52, routeExposure: 38, riverProximity: 42 } },
    { location: [19.067, 72.868] as [number, number], factors: { rainfall: 82, forecast: 84, floodExposure: 76, officialWarning: 74, routeExposure: 78, riverProximity: 68 } },
    { location: [19.061, 72.864] as [number, number], factors: { rainfall: 96, forecast: 94, floodExposure: 92, officialWarning: 96, routeExposure: 94, riverProximity: 88 } },
  ];
  const scenario = scenarios[Math.min(Math.max(step, 0), scenarios.length - 1)];
  return { step: Math.min(Math.max(step, 0), scenarios.length - 1), ...scenario, risk: calculateRisk(scenario.factors) };
}
