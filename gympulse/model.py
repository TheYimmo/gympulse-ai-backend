"""SCRUM-32 — Entrenamiento y evaluación del modelo XGBoost (US02)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from gympulse.config import DEFAULT_CSV, REPORTS_DIR
from gympulse.features import FEATURE_COLS, TARGET_COL, build_feature_matrix
from gympulse.splits import split_xy, temporal_split

MODEL_REPORT = REPORTS_DIR / "reporte_modelo_scrum32.json"

XGBOOST_PARAMS = {
    "n_estimators": 800,
    "max_depth": 5,
    "learning_rate": 0.03,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "gamma": 0.0,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "n_jobs": -1,
}


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def train_model(
    csv_path: Path | None = None,
) -> tuple[XGBRegressor, dict]:
    """Entrena XGBoost y devuelve (modelo, métricas)."""
    df, region_codes = build_feature_matrix(csv_path)
    train, val, test = temporal_split(df)

    X_train, y_train = split_xy(train, FEATURE_COLS, TARGET_COL)
    X_val, y_val = split_xy(val, FEATURE_COLS, TARGET_COL)
    X_test, y_test = split_xy(test, FEATURE_COLS, TARGET_COL)

    model = XGBRegressor(
        **XGBOOST_PARAMS,
        eval_metric="rmse",
        early_stopping_rounds=60,
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    def _metrics(X, y, split_name):
        pred = model.predict(X)
        return {
            "split": split_name,
            "n_samples": len(y),
            "mape_pct": round(_mape(y.values, pred), 4),
            "rmse": round(_rmse(y.values, pred), 6),
        }

    metrics = {
        "train": _metrics(X_train, y_train, "train"),
        "val": _metrics(X_val, y_val, "val"),
        "test": _metrics(X_test, y_test, "test"),
    }

    importances = dict(
        zip(
            FEATURE_COLS,
            model.feature_importances_.round(4).tolist(),
        )
    )

    report = {
        "jira_issue": "SCRUM-32",
        "model": "XGBoost",
        "target": TARGET_COL,
        "horizon_years": 3,
        "xgboost_params": XGBOOST_PARAMS,
        "best_iteration": int(model.best_iteration),
        "metrics": metrics,
        "feature_importances": importances,
        "region_encoding": region_codes,
        "mape_val_pct": metrics["val"]["mape_pct"],
        "mape_test_pct": metrics["test"]["mape_pct"],
        "criterio_superado": metrics["val"]["mape_pct"] < 6.0,
    }

    return model, report


def save_model_report(
    csv_path: Path | None = None,
    output_path: Path | None = None,
) -> tuple[XGBRegressor, Path]:
    model, report = train_model(csv_path)
    REPORTS_DIR.mkdir(exist_ok=True)
    target = output_path or MODEL_REPORT
    with target.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return model, target


def predict_country(
    model: XGBRegressor,
    df_full: pd.DataFrame,
    country: str,
    base_year: int,
    region_codes: dict,
) -> list[dict]:
    """Genera proyecciones de penetración para un país desde base_year."""
    row = df_full[(df_full["country"] == country) & (df_full["year"] == base_year)]
    if row.empty:
        raise ValueError(f"No data for {country} year {base_year}")

    row = row.iloc[0]

    prev = df_full[(df_full["country"] == country) & (df_full["year"] == base_year - 1)]
    prev_pen = float(prev.iloc[0]["gym_penetration_rate"]) if not prev.empty else row["gym_penetration_rate"]
    prev2 = df_full[(df_full["country"] == country) & (df_full["year"] == base_year - 2)]
    prev2_pen = float(prev2.iloc[0]["gym_penetration_rate"]) if not prev2.empty else prev_pen
    curr_pen = float(row["gym_penetration_rate"])

    features = {
        "year": base_year,
        "gym_penetration_rate": curr_pen,
        "gym_penetration_rate_lag1": prev_pen,
        "gym_penetration_rate_lag2": prev2_pen,
        "penetration_rolling_mean3": (curr_pen + prev_pen + prev2_pen) / 3,
        "penetration_yoy_change": curr_pen - prev_pen,
        "covid_indicator": int(base_year in (2020, 2021)),
        "gdp_per_capita_usd": float(row["gdp_per_capita_usd"]),
        "gdp_growth_rate": 0.0,
        "urban_population_percentage": float(row["urban_population_percentage"]),
        "obesity_rate": float(row["obesity_rate"]),
        "fitness_participation_rate": float(row["fitness_participation_rate"]),
        "insufficient_physical_activity_pct": float(row["insufficient_physical_activity_pct"]),
        "average_membership_cost_usd": float(row["average_membership_cost_usd"]),
        "population_total": float(row["population_total"]),
        "region_encoded": region_codes.get(row["region"], 0),
    }

    X = pd.DataFrame([features])[FEATURE_COLS]
    pred = float(model.predict(X)[0])

    return [
        {
            "country": country,
            "base_year": base_year,
            "predicted_year": base_year + 3,
            "predicted_penetration_rate": round(pred, 6),
        }
    ]


def main() -> None:
    _, out = save_model_report()
    print(f"Modelo SCRUM-32 entrenado. Reporte: {out}")
