"""SCRUM-6 / SCRUM-10 / SCRUM-34 — FastAPI entrypoint."""

from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.database import SessionLocal, init_db, ping_database
from app.routers import predict

app = FastAPI(
    title="GymPulse AI",
    version="2.0",
    description=(
        "API de análisis y predicción de penetración de gimnasios a nivel global. "
        "Sprint 2: modelo XGBoost con horizonte de 3 años para 132 países."
    ),
)

app.include_router(predict.router)

init_db()


@app.get("/")
def read_root():
    return {
        "proyecto": "GymPulse AI",
        "sprint": 2,
        "equipo": 31,
        "estado": "Operativo",
        "documentacion": "Navega a /docs para interactuar con la API",
        "endpoints_ml": ["/predict/penetration", "/predict/countries", "/predict/penetration/batch"],
    }


@app.get("/health")
def health_check():
    connected = ping_database()
    return {
        "status": "ok" if connected or not SessionLocal else "degraded",
        "database": "connected" if connected else "not_configured",
    }


@app.get("/countries")
def get_countries():
    if not SessionLocal:
        return {"error": "Base de datos no conectada"}

    db = SessionLocal()
    try:
        result = db.execute(text("SELECT DISTINCT country FROM gym_metrics ORDER BY country")).fetchall()
        countries = [row[0] for row in result]
        return {"total_paises": len(countries), "countries": countries}
    finally:
        db.close()


@app.get("/metrics/{country}")
def get_metrics(country: str):
    """SCRUM-10 / SCRUM-26 — Series temporales por país."""
    if not SessionLocal:
        raise HTTPException(status_code=503, detail="Base de datos no conectada")

    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT year, region, gym_memberships, fitness_participation_rate,
                       gym_penetration_rate, gdp_per_capita_usd, obesity_rate
                FROM gym_metrics
                WHERE country = :country
                ORDER BY year
            """),
            {"country": country},
        ).mappings().all()

        if not rows:
            raise HTTPException(status_code=404, detail=f"País no encontrado: {country}")

        return {
            "country": country,
            "region": rows[0]["region"],
            "total_years": len(rows),
            "metrics": [dict(r) for r in rows],
        }
    finally:
        db.close()
