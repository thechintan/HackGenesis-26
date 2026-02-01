from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
import datetime

# Import the ranking service
from ..services.alert_ranking import rank_alerts

router = APIRouter(tags=["Alerts"])

import random # Add random import

@router.get("/alerts")
def get_alerts(lat: float = None, lon: float = None, radius_km: float = 50, db: Session = Depends(get_db)):
    """
    Get active alerts.
    - If lat/lon provided: Fetches LIVE data from external APIs (Weather, Earthquakes).
    - If not: Returns general stored alerts.
    """
    
    response = []
    
    # 1. LIVE DATA FETCH (Priority)
    if lat is not None and lon is not None:
        try:
            from ..services.live_data import get_real_time_alerts
            live_alerts = get_real_time_alerts(lat, lon)
            
            # Define IST timezone
            IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

            # Convert to response format
            for a in live_alerts:
                response.append({
                    "id": random.randint(1000, 9999), # Temp ID for frontend
                    "location": "Nearby Region",
                    "lat": a.get("lat", lat), 
                    "lon": a.get("lon", lon),
                    "title": a["title"],
                    "message": a["message"],
                    "severity": a["severity"],
                    "alert_type": a["type"],
                    "source": a["source"],
                    "created_at": datetime.datetime.now(IST),
                    "distance_km": 0, # Calculated client side or roughly here
                    "cpi": 50, # dynamic calc needed ideally
                    "priority_score": 100 if a["severity"] == "High" else 50
                })
        except Exception as e:
            print(f"Live fetch failed: {e}")

    # 2. DATABASE ALERTS (Community Reports & Persistence)
    # We still want community reports from the DB
    db_alerts = db.query(Alert).all()
    
    if lat is not None and lon is not None:
        ranked_db = rank_alerts(db_alerts, lat, lon)
        for r in ranked_db:
            # Add DB alerts to the list
             response.append({
                "id": r["alert"].id,
                "location": r["alert"].location,
                "lat": r["alert"].lat,
                "lon": r["alert"].lon,
                "title": r["alert"].title,
                "message": r["alert"].message,
                "severity": r["alert"].severity,
                "alert_type": r["alert"].alert_type,
                "source": r["alert"].source,
                "created_at": r["alert"].created_at,
                "distance_km": r["distance_km"],
                "cpi": r["cpi"],
                "priority_score": r["priority_score"]
            })
    else:
        # Fallback if no location
        for a in db_alerts:
             response.append({
                "id": a.id,
                "location": a.location,
                "lat": a.lat,
                "lon": a.lon,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "alert_type": a.alert_type,
                "source": a.source,
                "created_at": a.created_at,
                "distance_km": 0,
                "cpi": 0,
                "priority_score": 0
            })

    # Deduplicate or Sort?
    # For now, put High Severity text to top
    response.sort(key=lambda x: 1 if x["severity"] == 'High' else 2)
    
    return response

# Removed seed_alerts call for purely live + db approach, or logic can remain separate
@router.get("/heatmap")
def get_heatmap_data():
    from ..ai_logic import generate_heatmap_data
    return generate_heatmap_data()
