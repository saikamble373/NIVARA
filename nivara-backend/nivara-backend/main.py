"""
NIVARA Backend - Member 4 (Backend + Risk Engine)

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then open:
    http://localhost:8000/docs   <- interactive API docs (auto-generated),
                                     send this link to Members 2, 3, 5, 6
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import weather, hazards, risk, route_risk, simulation, recommendation, alerts

app = FastAPI(
    title="NIVARA Backend",
    description="AI-Powered Personal Disaster Risk & Decision Support System - Risk Engine API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(hazards.router)
app.include_router(risk.router)
app.include_router(route_risk.router)
app.include_router(simulation.router)
app.include_router(recommendation.router)
app.include_router(alerts.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "NIVARA backend", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
