import { describe, expect, it } from "vitest";
import { calculateRisk, getRiskLevel, getSimulationStep, ROUTES } from "@shared/nivara";

describe("NIVARA risk engine", () => {
  it("applies the documented weighted factors", () => {
    const result = calculateRisk({ rainfall: 100, forecast: 100, floodExposure: 100, officialWarning: 100, routeExposure: 100, riverProximity: 100 });
    expect(result.score).toBe(100);
    expect(result.level).toBe("CRITICAL");
  });

  it("uses the documented risk thresholds", () => {
    expect(getRiskLevel(30)).toBe("LOW");
    expect(getRiskLevel(31)).toBe("MODERATE");
    expect(getRiskLevel(60)).toBe("MODERATE");
    expect(getRiskLevel(61)).toBe("HIGH");
    expect(getRiskLevel(80)).toBe("HIGH");
    expect(getRiskLevel(81)).toBe("CRITICAL");
  });

  it("keeps official-warning guidance ahead of personalized optimization", () => {
    const result = calculateRisk({ rainfall: 5, forecast: 5, floodExposure: 5, officialWarning: 100, routeExposure: 5, riverProximity: 5 });
    expect(result.reasons).toContain("Official warning is active");
    expect(result.recommendation).toContain("official emergency guidance");
  });

  it("compares route exposure and identifies the safer alternative", () => {
    expect(ROUTES.current.exposed).toBeGreaterThan(ROUTES.alternative.exposed);
    expect(ROUTES.current.risk).toBeGreaterThan(ROUTES.alternative.risk);
    expect(ROUTES.alternative.severity).toBe("LOW");
  });

  it("progresses simulation states with the same engine", () => {
    const levels = [0, 1, 2, 3].map((step) => getSimulationStep(step).risk.level);
    expect(levels).toEqual(["LOW", "MODERATE", "HIGH", "CRITICAL"]);
  });
});
