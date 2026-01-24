from ..utils.geo import haversine
from ..utils.severity import severity_weight
from ..utils.cpi import estimate_cpi

def rank_alerts(alerts, user_lat, user_lon):
    ranked = []

    for alert in alerts:
        distance = haversine(user_lat, user_lon, alert.lat, alert.lon)
        severity = severity_weight(alert.severity)
        cpi = estimate_cpi(alert.alert_type)

        priority_score = (
            0.5 * severity +
            0.3 * max(0, 100 - distance) +   # nearer = higher score
            0.2 * cpi
        )

        ranked.append({
            "alert": alert,
            "distance_km": round(distance, 2),
            "cpi": cpi,
            "priority_score": round(priority_score, 2)
        })

    # Sort by priority score descending
    ranked.sort(key=lambda x: x["priority_score"], reverse=True)
    return ranked
