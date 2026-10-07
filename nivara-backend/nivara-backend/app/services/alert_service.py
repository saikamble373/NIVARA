"""
Smart Alerts service. Decides whether a risk update deserves a push
alert, and formats the message. Kept deliberately simple/rule-based
so Member 6 can wire it straight into a toast/notification component.
"""
from app.models.schemas import AlertResponse

ALERT_THRESHOLD_SCORE = 61  # HIGH and above triggers an alert


def build_alert(location_label: str, risk_score: float, risk_level: str, reasons: list) -> AlertResponse:
    should_alert = risk_score >= ALERT_THRESHOLD_SCORE

    if not should_alert:
        return AlertResponse(
            should_alert=False,
            severity="info",
            alert_message=f"{location_label}: risk is {risk_level} ({risk_score}/100). No alert needed.",
        )

    severity = "critical" if risk_level == "CRITICAL" else "warning"
    reason_text = f" {reasons[0]}" if reasons else ""
    message = f"{risk_level} RISK at {location_label} ({risk_score}/100).{reason_text} Take precaution."

    return AlertResponse(
        should_alert=True,
        severity=severity,
        alert_message=message,
    )
