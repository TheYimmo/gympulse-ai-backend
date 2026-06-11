"""SCRUM-9 — Reporte de calidad de datos."""

import json
from pathlib import Path

import pandas as pd

from gympulse.config import DEFAULT_CSV, QUALITY_REPORT, REPORTS_DIR
from gympulse.constants import METRICS


def _outliers_iqr(series: pd.Series) -> dict:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (series < lower) | (series > upper)
    return {
        "count": int(mask.sum()),
        "lower_bound": float(lower),
        "upper_bound": float(upper),
    }


def build_quality_report(csv_path: Path | None = None) -> dict:
    path = csv_path or DEFAULT_CSV
    df = pd.read_csv(path)

    nulls_by_region = (
        df.groupby("region")[list(METRICS)]
        .apply(lambda g: g.isnull().sum())
        .to_dict()
    )

    outliers_by_region: dict = {}
    for region, group in df.groupby("region"):
        outliers_by_region[region] = {
            col: _outliers_iqr(group[col].dropna())
            for col in METRICS
            if group[col].notna().any()
        }

    return {
        "jira_issue": "SCRUM-9",
        "source_file": str(path),
        "total_registros": int(len(df)),
        "valores_nulos_por_columna": df.isnull().sum().to_dict(),
        "valores_nulos_por_region": nulls_by_region,
        "atipicos_iqr_por_region": outliers_by_region,
        "resumen_estadistico": df.describe().to_dict(),
        "regiones": sorted(df["region"].unique().tolist()),
        "paises": int(df["country"].nunique()),
    }


def save_quality_report(
    csv_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    report = build_quality_report(csv_path)
    REPORTS_DIR.mkdir(exist_ok=True)
    target = output_path or QUALITY_REPORT
    with target.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return target


def main() -> None:
    out = save_quality_report()
    print(f"Reporte SCRUM-9 generado: {out}")
