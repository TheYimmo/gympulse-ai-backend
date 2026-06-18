"""SCRUM-30 — Pipeline de feature engineering para modelos ML."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from gympulse.config import DEFAULT_CSV
from gympulse.constants import METRICS

FEATURE_COLS = [
    "year",
    "gym_penetration_rate",
    "gym_penetration_rate_lag1",
    "gym_penetration_rate_lag2",
    "penetration_rolling_mean3",
    "penetration_yoy_change",
    "covid_indicator",
    "gdp_per_capita_usd",
    "gdp_growth_rate",
    "urban_population_percentage",
    "obesity_rate",
    "fitness_participation_rate",
    "insufficient_physical_activity_pct",
    "average_membership_cost_usd",
    "population_total",
    "region_encoded",
]

TARGET_COL = "target_penetration_3y"
HORIZON = 3  # años hacia el futuro


def build_feature_matrix(
    csv_path: Path | None = None,
    horizon: int = HORIZON,
) -> pd.DataFrame:
    """Construye la matriz de features y target para XGBoost.

    Cada fila es (country, base_year) con features del año base
    y target = gym_penetration_rate en base_year + horizon.
    """
    path = csv_path or DEFAULT_CSV
    df = pd.read_csv(path).sort_values(["country", "year"]).reset_index(drop=True)

    # --- lag features por país ---
    df["gym_penetration_rate_lag1"] = df.groupby("country")[
        "gym_penetration_rate"
    ].shift(1)
    df["gym_penetration_rate_lag2"] = df.groupby("country")[
        "gym_penetration_rate"
    ].shift(2)

    # --- rolling mean (ventana 3 años centrada en t) ---
    df["penetration_rolling_mean3"] = (
        df.groupby("country")["gym_penetration_rate"]
        .transform(lambda s: s.rolling(3, min_periods=1).mean())
    )

    # --- cambio año a año ---
    df["penetration_yoy_change"] = df.groupby("country")[
        "gym_penetration_rate"
    ].diff(1).fillna(0)

    # --- indicador de disrupción COVID (2020-2021) ---
    df["covid_indicator"] = df["year"].isin([2020, 2021]).astype(int)

    # --- tasa de crecimiento del GDP ---
    df["gdp_growth_rate"] = df.groupby("country")[
        "gdp_per_capita_usd"
    ].pct_change(1).fillna(0)

    # --- target: penetración en t + horizon ---
    df["target_penetration_3y"] = df.groupby("country")[
        "gym_penetration_rate"
    ].shift(-horizon)

    # --- codificación de región ---
    region_codes = {r: i for i, r in enumerate(sorted(df["region"].unique()))}
    df["region_encoded"] = df["region"].map(region_codes)

    # eliminar filas sin target o sin lags mínimos
    df = df.dropna(subset=["target_penetration_3y", "gym_penetration_rate_lag1"])

    meta_cols = ["country", "year", "region"]
    extra_feature_cols = [c for c in FEATURE_COLS if c not in meta_cols]
    df = df[meta_cols + extra_feature_cols + [TARGET_COL]].reset_index(drop=True)

    return df, region_codes
