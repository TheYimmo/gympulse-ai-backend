import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="GymPulse AI - Sprint 1", version="1.0")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None
Base = declarative_base()

if DATABASE_URL:
    url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SCRUM-7: Esquema de base de datos exacto según tu CSV
class GymData(Base):
    __tablename__ = "gym_metrics"
    # SQLAlchemy requiere una llave primaria por defecto
    id = Column(Integer, primary_key=True, autoincrement=True) 
    country = Column(String, index=True)
    year = Column(Integer)
    region = Column(String)
    gym_memberships = Column(Float)
    fitness_participation_rate = Column(Float)
    total_health_club_revenue_usd = Column(Float)
    number_of_gyms = Column(Float)
    gym_penetration_rate = Column(Float)
    urban_population_percentage = Column(Float)
    obesity_rate = Column(Float)
    gdp_per_capita_usd = Column(Float)
    population_total = Column(Float)
    average_membership_cost_usd = Column(Float)
    insufficient_physical_activity_pct = Column(Float)

if engine:
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {
        "proyecto": "GymPulse AI",
        "sprint": 1,
        "equipo": 31,
        "estado": "Operativo. Base de datos conectada al 100%.",
        "documentacion": "Navega a /docs para interactuar con la API"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "database": "connected" if engine else "not_configured"}

@app.get("/countries")
def get_countries():
    # SCRUM-10: Consulta a la BD real
    if not SessionLocal:
        return {"error": "Base de datos no conectada"}
    
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT DISTINCT country FROM gym_metrics")).fetchall()
        countries = [row[0] for row in result]
        return {"total_paises": len(countries), "countries": countries}
    finally:
        db.close()