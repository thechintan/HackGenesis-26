from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
import datetime

# Import the ranking service
from ..services.alert_ranking import rank_alerts

router = APIRouter(tags=["Alerts"])

@router.get("/alerts")
def get_alerts(lat: float = None, lon: float = None, radius_km: float = 50, db: Session = Depends(get_db)):
    """
    Get active alerts.
    - If lat/lon provided: Returns ranked alerts sorted by priority/distance AND filtered by radius.
    - If not: Returns all alerts sorted by severity.
    """
    # Always regenerate for 'real-time' demo effect
    seed_alerts(db)
        
    alerts = db.query(Alert).all()
    
    if lat is not None and lon is not None:
        # Use the ranking logic
        ranked_alerts = rank_alerts(alerts, lat, lon)
        
        # Filter by radius and format
        response = []
        for r in ranked_alerts:
            if r["distance_km"] <= radius_km:
                response.append({
                    "id": r["alert"].id,
                    "location": r["alert"].location,
                    "lat": r["alert"].lat,
                    "lon": r["alert"].lon,
                    "title": r["alert"].title,
                    "message": r["alert"].message,
                    "severity": r["alert"].severity,
                    "alert_type": r["alert"].alert_type,
                    "created_at": r["alert"].created_at,
                    "distance_km": r["distance_km"],
                    "cpi": r["cpi"],
                    "priority_score": r["priority_score"]
                })
        return response
    else:
        # Fallback to simple sort by severity if no location provided
        return sorted(alerts, key=lambda a: 1 if a.severity == 'High' else 2)

def seed_alerts(db: Session):
    from ..ai_logic import generate_dynamic_alerts
    # Clear existing to simulation 'live' refresh
    db.query(Alert).delete()
    
    dynamic_data = generate_dynamic_alerts()
    
    alerts = [
        Alert(
            location=d["location"],
            lat=d["lat"],
            lon=d["lon"],
            title=d["title"],
            message=d["message"],
            severity=d["severity"],
            alert_type=d["alert_type"]
        )
        for d in dynamic_data
    ]
    db.add_all(alerts)
    db.commit()

@router.get("/heatmap")
def get_heatmap_data():
    from ..ai_logic import generate_heatmap_data
    return generate_heatmap_data()
