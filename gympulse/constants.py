"""Columnas del dataset clean_gym_data.csv."""

DIMENSIONS = ("country", "year", "region")

METRICS = (
    "gym_memberships",
    "fitness_participation_rate",
    "total_health_club_revenue_usd",
    "number_of_gyms",
    "gym_penetration_rate",
    "urban_population_percentage",
    "obesity_rate",
    "gdp_per_capita_usd",
    "population_total",
    "average_membership_cost_usd",
    "insufficient_physical_activity_pct",
)

ALL_COLUMNS = DIMENSIONS + METRICS
