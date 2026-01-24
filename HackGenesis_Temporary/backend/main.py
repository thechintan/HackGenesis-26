from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, posts, alerts, authority, trends
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coastal Threat Alert System API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(alerts.router)
app.include_router(authority.router)
app.include_router(trends.router)

# Mount static files (Frontend)
# Serve HTML files from parent directory
import os
from fastapi.responses import FileResponse

frontend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Serve frontend.html as the default index
@app.get("/", response_class=FileResponse)
async def root():
    return os.path.join(frontend_dir, "frontend.html")

# Mount remaining static files
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8001, reload=False)