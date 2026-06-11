"""SCRUM-7 — Esquema SQLAlchemy."""

from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class GymData(Base):
    __tablename__ = "gym_metrics"

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
