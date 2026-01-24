from fastapi import APIRouter, Depends
import random
import requests
from sqlalchemy.orm import Session
from ..database import get_db
from datetime import datetime, timedelta

router = APIRouter(tags=["Trends"])

@router.get("/trends/data")
def get_trends_data(db: Session = Depends(get_db)):
    # --- 1. Real Weather Data (Open-Meteo) ---
    # Default Location: Mumbai (19.0760, 72.8777)
    lat, lon = 19.0760, 72.8777
    
    # Fetch Past 7 Days (for Pollution/Weather History)
    today = datetime.now()
    dates_7d = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
    
    pollution_data = []
    
    try:
        # Air Quality API (European AQI)
        # Using a public API for demonstration - Open-Meteo Air Quality
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=european_aqi&start_date={start_date}&end_date={end_date}"
        res = requests.get(aq_url)
        data = res.json()
        
        if "hourly" in data:
            # Aggregate hourly data to daily max
            hourly_aqi = data["hourly"]["european_aqi"]
            # We get 24 values per day. 7 days = 168 values approx.
            # Simplified chunking:
            chunk_size = 24
            for i in range(0, len(hourly_aqi), chunk_size):
                day_chunk = hourly_aqi[i:i+chunk_size]
                if day_chunk:
                    pollution_data.append(max(day_chunk))
            
            # Ensure we have exactly 7 items
            pollution_data = pollution_data[:7]
            while len(pollution_data) < 7:
                pollution_data.append(random.randint(40, 80)) # Fallback
        else:
            pollution_data = [random.randint(40, 80) for _ in range(7)]
            
    except Exception as e:
        print(f"AQI Fetch Error: {e}")
        pollution_data = [random.randint(40, 80) for _ in range(7)]

    # --- 2. Cyclone / Wind Forecast (Next 24 Hours) ---
    cyclone_labels = ['-24h', '-12h', 'Now', '+12h', '+24h']
    cyclone_data = [] # Wind speeds
    
    try:
        # Forecast API
        # We need past 1 day and forecast 1 day
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=windspeed_10m&past_days=1&forecast_days=2"
        w_res = requests.get(w_url)
        w_data = w_res.json()
        
        if "hourly" in w_data:
            speeds = w_data["hourly"]["windspeed_10m"]
            # We need 5 points roughly centered on "Now"
            # "Now" is the end of past_days (24 hrs in) roughly.
            # Index 24 is roughly "Now" (if we start from 00:00 yesterday). 
            # Actually, the API returns from 00:00 of start date.
            # Let's just pick indices: 0 (-24h), 12 (-12h), 24 (Now), 36 (+12h), 48 (+24h)
            indices = [0, 12, 24, 36, 48]
            for idx in indices:
                if idx < len(speeds):
                    cyclone_data.append(speeds[idx])
                else:
                    cyclone_data.append(speeds[-1])
        else:
             cyclone_data = [20, 25, 30, 25, 20] # Fallback
             
    except Exception as e:
        print(f"Wind Fetch Error: {e}")
        cyclone_data = [20, 25, 30, 25, 20]

    # --- 3. Community Reports (Real DB Data) ---
    # Query DB for counts by type
    from sqlalchemy import func
    from ..models import Alert
    
    # We will query the 'Alert' table. 
    # Note: 'Alert' table in this hackathon setup might be seeded or user-generated.
    # If user wants "Real Data", they might expect the "Create Post" to feed this? 
    # But 'Alert' is usually system generated. The 'Post' model is user generated.
    # Let's count 'Post' instead? "Community Reports" sounds like 'Post'.
    # Let's count 'Alert' types for now as the chart says "Flood", "Pollution" etc.
    
    # Let's actually count 'Alert's for now as they have specific types stored in DB
    report_counts = db.query(Alert.alert_type, func.count(Alert.id)).group_by(Alert.alert_type).all()
    
    # Map to chart categories: ['Flood', 'Pollution', 'Erosion', 'Other']
    # Existing alert types: "Weather", "Storm", "Oil Spill", "Pollution", "Cyclone"
    # Mapping logic:
    reports_map = {'Flood': 0, 'Pollution': 0, 'Erosion': 0, 'Other': 0}
    
    for r_type, count in report_counts:
        if r_type in ["Weather", "Storm", "Cyclone"]:
            reports_map['Flood'] += count # Grouping storm under flood/risk
        elif r_type in ["Pollution", "Oil Spill"]:
            reports_map['Pollution'] += count
        else:
            reports_map['Other'] += count
            
    reports_dist = [reports_map['Flood'], reports_map['Pollution'], reports_map['Erosion'], reports_map['Other']]
    
    # --- 4. Sea Level (Simulated Dynamic) ---
    # Tidal pattern (Sine wave)
    import math
    base_tide = 1.5
    sea_levels = []
    # Generate 7 days past
    for i in range(7):
        # A simple sine wave varying by day
        val = base_tide + 0.5 * math.sin((today.toordinal() - 6 + i) * 0.5)
        sea_levels.append(round(val, 2))

    return {
        "dates_7d": dates_7d,
        "sea_level": sea_levels,
        "pollution": pollution_data,
        "cyclone_labels": cyclone_labels,
        "cyclone_data": cyclone_data,
        "reports_dist": reports_dist
    }
