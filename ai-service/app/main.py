from fastapi import FastAPI
from app.database import engine

app = FastAPI(
    title="Smart Space AI & Analytics Engine",
    description="Python FastAPI service for Smart Space occupancy and utilization analytics.",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "Smart Space AI Service",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
