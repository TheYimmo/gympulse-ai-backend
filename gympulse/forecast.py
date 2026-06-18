"""SCRUM-35 — Proyecciones de penetración e ingresos hacia 2029."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from gympulse.config import DEFAULT_CSV, REPORTS_DIR
from gympulse.features import FEATURE_COLS, build_feature_matrix
from gympulse.model import save_model_report

FORECAST_CSV = REPORTS_DIR / "forecast_2026_2029.csv"
FORECAST_JSON = REPORTS_DIR / "reporte_forecast_scrum35.json"

# Base years available in dataset; each predicts base_year + 3
FORECAST_BASE_YEARS = [2023, 2024, 2025, 2026]


def _build_row(df_raw: pd.DataFrame, country: str, base_year: int, region_codes: dict) -> dict | None:
    row = df_raw[(df_raw["country"] == country) & (df_raw["year"] == base_year)]
    if row.empty:
        return None
    row = row.iloc[0]

    prev = df_raw[(df_raw["country"] == country) & (df_raw["year"] == base_year - 1)]
    prev_pen = float(prev.iloc[0]["gym_penetration_rate"]) if not prev.empty else float(row["gym_penetration_rate"])
    prev2 = df_raw[(df_raw["country"] == country) & (df_raw["year"] == base_year - 2)]
    prev2_pen = float(prev2.iloc[0]["gym_penetration_rate"]) if not prev2.empty else prev_pen
    curr_pen = float(row["gym_penetration_rate"])

    prev_gdp = df_raw[(df_raw["country"] == country) & (df_raw["year"] == base_year - 1)]
    prev_gdp_val = float(prev_gdp.iloc[0]["gdp_per_capita_usd"]) if not prev_gdp.empty else float(row["gdp_per_capita_usd"])
    gdp_growth = (float(row["gdp_per_capita_usd"]) - prev_gdp_val) / prev_gdp_val if prev_gdp_val != 0 else 0.0

    return {
        "year": base_year,
        "gym_penetration_rate": curr_pen,
        "gym_penetration_rate_lag1": prev_pen,
        "gym_penetration_rate_lag2": prev2_pen,
        "penetration_rolling_mean3": (curr_pen + prev_pen + prev2_pen) / 3,
        "penetration_yoy_change": curr_pen - prev_pen,
        "covid_indicator": int(base_year in (2020, 2021)),
        "gdp_per_capita_usd": float(row["gdp_per_capita_usd"]),
        "gdp_growth_rate": gdp_growth,
        "urban_population_percentage": float(row["urban_population_percentage"]),
        "obesity_rate": float(row["obesity_rate"]),
        "fitness_participation_rate": float(row["fitness_participation_rate"]),
        "insufficient_physical_activity_pct": float(row["insufficient_physical_activity_pct"]),
        "average_membership_cost_usd": float(row["average_membership_cost_usd"]),
        "population_total": float(row["population_total"]),
        "region_encoded": region_codes.get(row["region"], 0),
    }


def generate_forecasts(
    csv_path: Path | None = None,
    model: XGBRegressor | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Genera proyecciones de penetración 2026-2029 para todos los países."""
    path = csv_path or DEFAULT_CSV
    df_raw = pd.read_csv(path).sort_values(["country", "year"]).reset_index(drop=True)

    _, region_codes = build_feature_matrix(path)

    if model is None:
        model, _ = save_model_report(path)

    countries = sorted(df_raw["country"].unique())
    rows = []

    for country in countries:
        region = df_raw[df_raw["country"] == country]["region"].iloc[0]
        for base_year in FORECAST_BASE_YEARS:
            feat = _build_row(df_raw, country, base_year, region_codes)
            if feat is None:
                continue
            X = pd.DataFrame([feat])[FEATURE_COLS]
            pred_pen = float(model.predict(X)[0])
            target_year = base_year + 3

            # Revenue proxy: penetration × population × avg_membership_cost × 12
            base_row = df_raw[(df_raw["country"] == country) & (df_raw["year"] == base_year)]
            if not base_row.empty:
                pop = float(base_row.iloc[0]["population_total"])
                avg_cost = float(base_row.iloc[0]["average_membership_cost_usd"])
                projected_revenue = pred_pen * pop * avg_cost * 12
            else:
                projected_revenue = None

            rows.append({
                "country": country,
                "region": region,
                "base_year": base_year,
                "target_year": target_year,
                "predicted_penetration_rate": round(pred_pen, 6),
                "projected_annual_revenue_usd": round(projected_revenue, 0) if projected_revenue else None,
            })

    df_forecast = pd.DataFrame(rows)

    summary_by_year = (
        df_forecast.groupby("target_year")["predicted_penetration_rate"]
        .agg(["mean", "min", "max", "median"])
        .round(4)
        .reset_index()
        .rename(columns={"mean": "mean_penetration", "min": "min_penetration",
                         "max": "max_penetration", "median": "median_penetration"})
        .to_dict("records")
    )

    top5_by_year = {}
    for yr in df_forecast["target_year"].unique():
        sub = df_forecast[df_forecast["target_year"] == yr]
        top5 = sub.nlargest(5, "predicted_penetration_rate")[
            ["country", "predicted_penetration_rate"]
        ].to_dict("records")
        top5_by_year[str(yr)] = top5

    report = {
        "jira_issue": "SCRUM-35",
        "forecast_base_years": FORECAST_BASE_YEARS,
        "forecast_target_years": [y + 3 for y in FORECAST_BASE_YEARS],
        "n_countries": len(countries),
        "total_projections": len(df_forecast),
        "summary_by_target_year": summary_by_year,
        "top5_penetration_by_target_year": top5_by_year,
    }

    return df_forecast, report


def save_forecasts(
    csv_path: Path | None = None,
    model: XGBRegressor | None = None,
) -> tuple[Path, Path]:
    df_forecast, report = generate_forecasts(csv_path, model)
    REPORTS_DIR.mkdir(exist_ok=True)
    df_forecast.to_csv(FORECAST_CSV, index=False)
    with FORECAST_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return FORECAST_CSV, FORECAST_JSON


def main() -> None:
    csv_out, json_out = save_forecasts()
    print(f"Proyecciones SCRUM-35 generadas:")
    print(f"  CSV:  {csv_out}")
    print(f"  JSON: {json_out}")
