"""SCRUM-51 — GET /predict/whatif para simulador económico What-If."""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.ml import get_model
from gympulse.features import FEATURE_COLS

router = APIRouter(prefix="/predict", tags=["Simulador What-If"])


def _build_features(row: pd.Series, year: int, df_raw: pd.DataFrame, country: str, region_codes: dict, gdp_factor: float = 1.0, obesity_factor: float = 1.0) -> pd.DataFrame:
    prev = df_raw[(df_raw["country"] == country) & (df_raw["year"] == year - 1)]
    prev_pen = float(prev.iloc[0]["gym_penetration_rate"]) if not prev.empty else float(row["gym_penetration_rate"])
    prev2 = df_raw[(df_raw["country"] == country) & (df_raw["year"] == year - 2)]
    prev2_pen = float(prev2.iloc[0]["gym_penetration_rate"]) if not prev2.empty else prev_pen
    curr_pen = float(row["gym_penetration_rate"])
    return pd.DataFrame([{
        "year": year,
        "gym_penetration_rate": curr_pen,
        "gym_penetration_rate_lag1": prev_pen,
        "gym_penetration_rate_lag2": prev2_pen,
        "penetration_rolling_mean3": (curr_pen + prev_pen + prev2_pen) / 3,
        "penetration_yoy_change": curr_pen - prev_pen,
        "covid_indicator": int(year in (2020, 2021)),
        "gdp_per_capita_usd": float(row["gdp_per_capita_usd"]) * gdp_factor,
        "gdp_growth_rate": 0.0,
        "urban_population_percentage": float(row["urban_population_percentage"]),
        "obesity_rate": float(row["obesity_rate"]) * obesity_factor,
        "fitness_participation_rate": float(row["fitness_participation_rate"]),
        "insufficient_physical_activity_pct": float(row["insufficient_physical_activity_pct"]),
        "average_membership_cost_usd": float(row["average_membership_cost_usd"]),
        "population_total": float(row["population_total"]),
        "region_encoded": region_codes.get(row["region"], 0),
    }])[FEATURE_COLS]


@router.get(
    "/whatif",
    summary="Simulador What-If: impacto de cambios en PIB y obesidad sobre penetración predicha",
    response_description="Escenario base vs. What-If con delta de penetración",
)
def predict_whatif(
    country: str = Query(..., description="País (nombre exacto del dataset)"),
    year: int = Query(2023, ge=2001, le=2026, description="Año base"),
    gdp_delta_pct: float = Query(0.0, ge=-50.0, le=100.0, description="Cambio % en PIB per cápita (ej. 10 = +10%)"),
    obesity_delta_pct: float = Query(0.0, ge=-30.0, le=50.0, description="Cambio % en tasa de obesidad (ej. -5 = -5%)"),
):
    model, df_raw, region_codes = get_model()

    available = sorted(df_raw["country"].unique().tolist())
    if country not in available:
        raise HTTPException(status_code=404, detail={"error": f"País '{country}' no encontrado.", "hint": "Consulta /predict/countries"})

    country_df = df_raw[df_raw["country"] == country]
    if year not in country_df["year"].unique().tolist():
        raise HTTPException(status_code=422, detail={"error": f"Año {year} no disponible para '{country}'."})

    row = country_df[country_df["year"] == year].iloc[0]
    gdp_factor = 1 + gdp_delta_pct / 100
    obesity_factor = 1 + obesity_delta_pct / 100

    base_pred = float(model.predict(_build_features(row, year, df_raw, country, region_codes))[0])
    whatif_pred = float(model.predict(_build_features(row, year, df_raw, country, region_codes, gdp_factor, obesity_factor))[0])

    delta = whatif_pred - base_pred
    delta_pct = round(delta / base_pred * 100, 4) if base_pred else 0.0

    return {
        "country": country,
        "region": row["region"],
        "base_year": year,
        "predicted_year": year + 3,
        "scenarios": {
            "base": {
                "gdp_per_capita_usd": round(float(row["gdp_per_capita_usd"]), 2),
                "obesity_rate": round(float(row["obesity_rate"]), 4),
                "predicted_penetration_rate": round(base_pred, 6),
            },
            "whatif": {
                "gdp_per_capita_usd": round(float(row["gdp_per_capita_usd"]) * gdp_factor, 2),
                "obesity_rate": round(float(row["obesity_rate"]) * obesity_factor, 4),
                "gdp_delta_pct": gdp_delta_pct,
                "obesity_delta_pct": obesity_delta_pct,
                "predicted_penetration_rate": round(whatif_pred, 6),
            },
        },
        "impact": {
            "penetration_delta": round(delta, 6),
            "penetration_delta_pct": delta_pct,
            "current_penetration_rate": round(float(row["gym_penetration_rate"]), 6),
        },
    }
