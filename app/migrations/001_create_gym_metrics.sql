-- SCRUM-7 / SCRUM-16 — Esquema gym_metrics
-- Ejecutado automáticamente por docker-compose en initdb

CREATE TABLE IF NOT EXISTS gym_metrics (
    id SERIAL PRIMARY KEY,
    country VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    region VARCHAR(255),
    gym_memberships DOUBLE PRECISION,
    fitness_participation_rate DOUBLE PRECISION,
    total_health_club_revenue_usd DOUBLE PRECISION,
    number_of_gyms DOUBLE PRECISION,
    gym_penetration_rate DOUBLE PRECISION,
    urban_population_percentage DOUBLE PRECISION,
    obesity_rate DOUBLE PRECISION,
    gdp_per_capita_usd DOUBLE PRECISION,
    population_total DOUBLE PRECISION,
    average_membership_cost_usd DOUBLE PRECISION,
    insufficient_physical_activity_pct DOUBLE PRECISION,
    CONSTRAINT uq_country_year UNIQUE (country, year)
);

CREATE INDEX IF NOT EXISTS ix_gym_metrics_country ON gym_metrics (country);
CREATE INDEX IF NOT EXISTS ix_gym_metrics_year ON gym_metrics (year);
CREATE INDEX IF NOT EXISTS ix_gym_metrics_region ON gym_metrics (region);
