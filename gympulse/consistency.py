"""SCRUM-11 — Reporte de consistencia país × año."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from gympulse.config import (
    CONSISTENCY_MATRIX,
    CONSISTENCY_SUMMARY,
    DEFAULT_CSV,
    EXPECTED_YEARS,
    QUALITY_REPORT,
    REPORTS_DIR,
)


def build_consistency_report(csv_path: Path | None = None) -> tuple[pd.DataFrame, dict]:
    path = csv_path or DEFAULT_CSV
    df = pd.read_csv(path)

    matrix = pd.crosstab(df["country"], df["year"])
    matrix = matrix.reindex(columns=EXPECTED_YEARS, fill_value=0).sort_index()

    gaps: list[dict] = []
    duplicates: list[dict] = []

    for country in matrix.index:
        for year in EXPECTED_YEARS:
            count = int(matrix.loc[country, year])
            if count == 0:
                gaps.append({"country": country, "year": year})
            elif count > 1:
                duplicates.append({"country": country, "year": year, "count": count})

    countries = int(df["country"].nunique())
    expected_cells = countries * len(EXPECTED_YEARS)
    complete_cells = int((matrix == 1).sum().sum())
    coverage_pct = round(100 * complete_cells / expected_cells, 2) if expected_cells else 0.0

    quality_ref = None
    if QUALITY_REPORT.exists():
        with QUALITY_REPORT.open(encoding="utf-8") as f:
            q = json.load(f)
        quality_ref = {
            "file": str(QUALITY_REPORT),
            "total_registros": q.get("total_registros"),
            "nulos_globales": sum(q.get("valores_nulos_por_columna", {}).values()),
        }

    summary = {
        "jira_issue": "SCRUM-11",
        "subtask": "SCRUM-28",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "file": str(path),
            "total_records": len(df),
            "unique_countries": countries,
            "unique_regions": int(df["region"].nunique()),
            "year_min": int(df["year"].min()),
            "year_max": int(df["year"].max()),
        },
        "consistency": {
            "expected_years": EXPECTED_YEARS,
            "expected_cells_country_year": expected_cells,
            "cells_with_exactly_one_record": complete_cells,
            "missing_cells": len(gaps),
            "duplicate_cells": len(duplicates),
            "coverage_percent": coverage_pct,
            "integrity_status": "PASS" if not gaps and not duplicates else "FAIL",
            "gaps": gaps,
            "duplicates": duplicates,
        },
        "cross_reference_scrum9": quality_ref,
        "outputs": {
            "matrix_csv": str(CONSISTENCY_MATRIX),
            "summary_json": str(CONSISTENCY_SUMMARY),
        },
        "po_approval": {
            "reviewer": "Carlos Pano Hernández (PO)",
            "status": "pending",
            "approved_at": None,
            "notes": "PO debe revisar gaps/duplicados y aprobar en SCRUM-11 antes de Sprint 2.",
        },
    }

    return matrix, summary


def save_consistency_report(csv_path: Path | None = None) -> dict:
    REPORTS_DIR.mkdir(exist_ok=True)
    matrix, summary = build_consistency_report(csv_path)

    matrix.to_csv(CONSISTENCY_MATRIX)

    with CONSISTENCY_SUMMARY.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Reporte consistencia país×año (SCRUM-11)")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Ruta al CSV fuente")
    args = parser.parse_args()

    summary = save_consistency_report(Path(args.csv))
    c = summary["consistency"]
    print(f"Reporte SCRUM-11 — estado: {c['integrity_status']}")
    print(f"  Países: {summary['source']['unique_countries']}")
    print(f"  Cobertura: {c['coverage_percent']}%")
    print(f"  Huecos: {c['missing_cells']} | Duplicados: {c['duplicate_cells']}")
    print(f"  Matriz: {CONSISTENCY_MATRIX}")
    print(f"  Resumen: {CONSISTENCY_SUMMARY}")
