# CoastalEye AI - Coastal Threat Alert System 🌊🚨

**CoastalEye AI** is a comprehensive disaster management and coastal monitoring platform designed to provide real-time alerts, community reporting, and authority response coordination. It empowers coastal communities and authorities to stay ahead of natural threats like cyclones, floods, and tsunamis.

## 🚀 Key Features

### 🌍 For the Community (Public Interface)
- **Live Threat Map**: Interactive map visualizing real-time wind, weather, and potential risk zones.
- **Satellite & IoT Data Integration**: Aggregates real-time sensor data from **Open-Meteo** (Satellite Weather) and **USGS** (Seismic IoT Sensors) to detect cyclones and tsunamis instantly.
- **Community Sentinel**: A social feed for users to report local hazards (with image uploads and geolocation).
- **Humanitarian Aid Hub**: Request emergency assistance (Medical, Food, Evacuation) with urgency levels.
- **Risk Trends**: Visual analytics of flood, storm, and tsunami risks over time.
- **My Activity Log**: Track the status of your reported posts and aid requests.

### 🛡️ For Authorities (Dashboard)
- **Centralized Command Center**: View and manage all incoming community reports and aid requests.
- **AI-Powered Prioritization**: Auto-ranking of alerts and requests based on severity and urgency scores.
- **Dispatch & Action**: Tools to dispatch teams, notify locals, or resolve incidents directly from the dashboard.
- **Role-Based Access**: Secure login specifically for authorized personnel (Coastal Admins).

## 🛠️ Technology Stack
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism Design), JavaScript (ES6+).
- **Backend**: Python (FastAPI).
- **Database**: SQLite (managed via SQLAlchemy).
- **Real-Time Data APIs**:
    - **Open-Meteo**: Satellite-based weather and wind speed data.
    - **USGS**: IoT Seismic Sensor networks for earthquake/tsunami detection.
    - **Leaflet**: Geospatial mapping.
- **Design**: Responsive, Dark-themed UI with `Inter` and `Playfair Display` typography.

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/thechintan/HackGenesis-26.git
    cd HackGenesis-26/HackGenesis_Temporary
    ```

2.  **Install Dependencies**
    Ensure you have Python installed. Install the required Python packages:
    ```bash
    pip install fastapi uvicorn sqlalchemy requests
    ```

3.  **Initialize the Database**
    Run the database manager to set up tables and create an admin user if needed:
    ```bash
    python manage_db.py
    # Select Option 5 (User) -> Option 5 (Create Test Admin User) to generate an admin account.
    ```
    *Default Admin Credentials:* `admin@coastal.com` / `admin123`

4.  **Run the Backend Server**
    Start the FastAPI server:
    ```bash
    python -m backend.main
    ```
    The server will start at `http://127.0.0.1:8001`.

5.  **Access the Application**
    Open `frontend.html` in your browser.
    *   **User View**: Sign up or log in to report incidents.
    *   **Authority View**: Log in with admin credentials to access the `authority_dashboard.html`.

## 📂 Project Structure
```
HackGenesis_Temporary/
├── backend/
│   ├── main.py            # FastAPI Entry point
│   ├── models.py          # Database Models
│   ├── ai_logic.py        # Logic for risk calculation & heatmap
│   └── routers/           # API Endpoints (auth, posts, alerts, etc.)
├── frontend.html          # Main User Landing Page
├── map.html               # Interactive Threat Map
├── authority_dashboard.html # Admin Control Panel
├── posts.html             # Community Feed
├── trends.html            # Data Visualization
└── manage_db.py           # CLI for Database Management
```

---
*Built for HackGenesis '26.*
