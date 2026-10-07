"""
Personalized Action Engine (rule-based, not ML - roadmap section 20).
Turns a risk score/level into concrete next-step actions for Member 6's UI.
"""
from app.models.schemas import RecommendationResponse


def get_recommendation(risk_score: float, risk_level: str,
                        route_hazardous: bool = False,
                        has_alt_route: bool = False) -> RecommendationResponse:

    if risk_level == "LOW":
        return RecommendationResponse(
            primary_action="proceed",
            actions=["Proceed as normal", "Stay updated on weather changes"],
            message="Conditions are currently safe. No action needed.",
        )

    if risk_level == "MODERATE":
        actions = ["Stay alert to changing conditions", "Avoid unnecessary travel through low-lying areas"]
        if route_hazardous:
            actions.append("Monitor your route for waterlogging")
        return RecommendationResponse(
            primary_action="monitor",
            actions=actions,
            message="Risk is moderate. Stay alert and monitor conditions before traveling.",
        )

    if risk_level == "HIGH":
        actions = ["Avoid the affected area if possible", "Delay travel if it is not urgent"]
        if has_alt_route:
            actions.append("Use the recommended alternative route")
        else:
            actions.append("Check for an alternative route before departing")
        actions.append("Check emergency resources near you")
        return RecommendationResponse(
            primary_action="avoid_or_reroute",
            actions=actions,
            message="High flood risk detected. Avoid the current route and delay travel if possible.",
        )

    # CRITICAL
    actions = [
        "Avoid the current route immediately",
        "Move to a safer location if you are in the hazard zone",
        "Use the safer alternative route" if has_alt_route else "Do not travel until conditions improve",
        "Check emergency resources and contacts now",
    ]
    return RecommendationResponse(
        primary_action="seek_safety",
        actions=actions,
        message="Critical risk. Avoid travel, move to safety, and check emergency resources immediately.",
    )
