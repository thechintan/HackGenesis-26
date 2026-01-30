import random
import math

def calculate_risk_score(text: str, location: str) -> int:
    """
    Advanced heuristic-based model to assign a risk score.
    Higher scores mean higher priority for authorities.
    """
    text_lower = text.lower()
    score = 0
    
    # Priority 1: Life-threatening / Disaster (60-100 pts)
    p1_keywords = ["tsunami", "cyclone", "flood", "drowning", "sos", "emergency", "earthquake"]
    for kw in p1_keywords:
        if kw in text_lower:
            score += 40
            
    # Priority 2: Health / Significant Threat (30-60 pts)
    p2_keywords = ["storm", "oil spill", "pollution", "hazard", "blocked", "bridge collapse"]
    for kw in p2_keywords:
        if kw in text_lower:
            score += 20
            
    # Priority 3: Environmental / Minor Anomaly (10-30 pts)
    p3_keywords = ["algal bloom", "waste", "trash", "erosion", "beach", "tide"]
    for kw in p3_keywords:
        if kw in text_lower:
            score += 10
            
    # Location context bonus (e.g., if it's a known high-risk shoreline)
    # Simple mock: if 'beach' is mentioned with a threat, it's more relevant
    if "beach" in text_lower or "shore" in text_lower:
        score += 5

    return min(score, 100)

def calculate_aid_priority(needs: str, description: str) -> str:
    """
    Determines urgency level (High, Medium, Low) for humanitarian aid.
    """
    combined = (needs + " " + description).lower()
    
    # High Priority: Life and Limb
    high_keywords = ["rescue", "trapped", "bleeding", "medical", "drowning", "ambulance", "stuck", "baby", "elderly"]
    for kw in high_keywords:
        if kw in combined:
            return "High"
            
    # Medium Priority: Essential needs
    med_keywords = ["food", "water", "shelter", "medicine", "pregnant", "fever", "electricity"]
    for kw in med_keywords:
        if kw in combined:
            return "Medium"
            
    return "Low"

def generate_heatmap_data():
    """
    Generates a global dataset approximating world coastlines.
    Simulates global satellite monitoring data.
    """
    points = []
    
    def add_line(start_lat, start_lon, end_lat, end_lon, steps, intensity_base, jitter=1.0):
        for i in range(steps):
            t = i / steps
            lat = start_lat * (1 - t) + end_lat * t
            lon = start_lon * (1 - t) + end_lon * t
            
            # Jitter to make it look less like a straight line
            lat += random.uniform(-jitter, jitter)
            lon += random.uniform(-jitter, jitter)
            
            # Intensity fluctuation
            intensity = max(0.1, min(1.0, intensity_base + random.uniform(-0.3, 0.3)))
            points.append([lat, lon, intensity])
            
    # Major Global Coastlines Approximations
    
    # 1. Americas West Coast (Alaska to Chile)
    # High risk in North (Storms) and Central (Hurricanes)
    add_line(60, -140, 30, -120, 40, 0.4)
    add_line(30, -120, 10, -90, 30, 0.7) # Central America (High)
    add_line(10, -90, -50, -75, 60, 0.5)

    # 2. Americas East Coast (Canada to Argentina)
    add_line(50, -60, 25, -80, 40, 0.5) # North Atlantic
    add_line(25, -80, 10, -75, 20, 0.9) # Caribbean (Very High Risk)
    add_line(10, -60, -40, -60, 50, 0.4) 

    # 3. Africa West Coast
    add_line(35, -10, 5, 5, 40, 0.3)
    add_line(5, 5, -34, 18, 50, 0.4)

    # 4. Africa East Coast
    add_line(-34, 25, 12, 50, 50, 0.6) # Cyclone zone

    # 5. Europe/Asia South Coast (Mediterranean -> India -> SE Asia)
    add_line(36, -5, 40, 25, 30, 0.3) # Med
    add_line(25, 60, 10, 75, 20, 0.7) # Arabian Sea
    add_line(10, 75, 20, 90, 20, 0.8) # Bay of Bengal (High)
    add_line(20, 90, 10, 105, 20, 0.7)
    add_line(10, 105, 35, 140, 40, 0.9) # Japan/SE Asia (Pacific Ring - High)

    # 6. Australia
    add_line(-20, 115, -35, 115, 20, 0.4) # West
    add_line(-35, 115, -35, 150, 30, 0.5) # South
    add_line(-35, 150, -10, 140, 30, 0.6) # East
    
    return points

def generate_dynamic_alerts():
    """
    Simulates real-time AI detection of threats.
    Returns a list of alert dictionaries.
    """
    base_threats = [
        {"loc": "Mumbai Coast", "lat": 19.0760, "lon": 72.8777, "type": "Cyclone", "title": "Cyclonic Swell Warning"},
        {"loc": "North Goa", "lat": 15.2993, "lon": 74.1240, "type": "Pollution", "title": "Algal Bloom Alert"},
        {"loc": "Coastal Kerala", "lat": 9.9312, "lon": 76.2673, "type": "Weather", "title": "Heavy Rainfall Advisory"},
        {"loc": "Chennai", "lat": 13.0827, "lon": 80.2707, "type": "Tsunami", "title": "Seismic Activity Alert"},
        {"loc": "Puri", "lat": 19.8135, "lon": 85.8312, "type": "Weather", "title": "High Tide Warning"},
        {"loc": "Gujarat Coast (Surat)", "lat": 21.1702, "lon": 72.8311, "type": "Flood", "title": "Tapi River Surge Alert"},
        {"loc": "Surat Beach (Dumas)", "lat": 21.0688, "lon": 72.7231, "type": "Weather", "title": "High Wind Alert"},
        {"loc": "Andaman", "lat": 11.7401, "lon": 92.6586, "type": "Storm", "title": "Tropical Storm Watch"}
    ]

    alerts_data = []
    # detailed messages
    messages = {
        "Cyclone": "Significant cyclonic activity detected. High waves expected.",
        "Pollution": "Harmful substance detected in water. Avoid contact.",
        "Weather": "Extreme weather conditions forecast for next 24 hours.",
        "Tsunami": "Undersea earthquake detected. Monitor coastal sirens.",
        "Oil Spill": "Satellite imagery confirms oil slick. Containment teams notified.",
        "Storm": "Tropical storm forming. Fishermen return to shore.",
        "Flood": "River levels rising rapidly due to upstream discharge. Evacuate low-lying areas."
    }

    # Randomly select 4-6 threats (increased slightly to ensure Surat likely appears or we can force it)
    active_threats = random.sample(base_threats, k=random.randint(4, 7))

    for t in active_threats:
        # Jitter location slightly
        lat_jitter = t["lat"] + random.uniform(-0.05, 0.05)
        lon_jitter = t["lon"] + random.uniform(-0.05, 0.05)
        
        # Random severity
        severity = random.choice(["High", "Medium", "Low"])
        
        # Simulated Source for "Integrated" feel
        sources = ["Sentinel-1 Satellite", "Coastal Buoy Sensor", "MetDept Radar", "Community Report", "IoT Network"]
        source = random.choice(sources)
        
        alerts_data.append({
            "location": t["loc"],
            "lat": lat_jitter,
            "lon": lon_jitter,
            "title": t["title"],
            "message": messages.get(t["type"], "Anomaly detected."),
            "severity": severity,
            "alert_type": t["type"],
            "source": source
        })
        
    return alerts_data
