import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI(title="GymPulse AI - Sprint 1", version="1.0")

# Render proporciona la URL de la base de datos en la variable DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/health")
def health_check():
    status = "ok"
    db_status = "connected"
    
    if DATABASE_URL:
        try:
            # Corregir prefijo de Render para SQLAlchemy si es necesario
            url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"error: {str(e)}"
            status = "unhealthy"
    else:
        db_status = "not_configured"

    return {
        "status": status,
        "database": db_status,
        "environment": "production" if DATABASE_URL else "local"
    }

@app.get("/countries")
def get_countries():
    # Endpoint requerido por SCRUM-10 (Estructura base)
    return {"countries": ["MEX", "USA", "BRA", "ARG", "CAN"]}

@app.get("/metrics/{country}")
def get_metrics(country: str):
    return {"country": country, "status": "pipeline_ready", "data": []}
