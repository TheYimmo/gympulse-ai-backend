"""SCRUM-8 — Pipeline ETL CSV → PostgreSQL."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from gympulse.config import DEFAULT_CSV, REPORTS_DIR, get_database_url

INGEST_REPORT = REPORTS_DIR / "reporte_ingesta_scrum21.json"


def load_csv(csv_path: Path | None = None) -> pd.DataFrame:
    path = csv_path or DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {path}")
    return pd.read_csv(path)


def validate_row_count(engine, table: str, expected: int) -> dict:
    """SCRUM-20 — Validar conteo CSV vs BD."""
    with engine.connect() as conn:
        db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    return {
        "expected_rows": expected,
        "db_rows": int(db_count),
        "match": int(db_count) == expected,
    }


def ingest_to_postgres(
    csv_path: Path | None = None,
    table: str = "gym_metrics",
    if_exists: str = "replace",
    validate: bool = True,
) -> dict:
    """Carga el CSV en PostgreSQL. Retorna métricas de la operación."""
    db_url = get_database_url()
    if not db_url:
        raise RuntimeError("Define DATABASE_URL antes de ejecutar la ingesta.")

    df = load_csv(csv_path)
    source_rows = len(df)

    engine = create_engine(db_url)
    df.to_sql(table, engine, if_exists=if_exists, index=False)

    result = {
        "source_file": str(csv_path or DEFAULT_CSV),
        "rows_inserted": source_rows,
        "table": table,
        "status": "ok",
    }

    if validate:
        validation = validate_row_count(engine, table, source_rows)
        result["validation"] = validation
        if not validation["match"]:
            result["status"] = "warning"
            print(f"Advertencia SCRUM-20: CSV={source_rows}, BD={validation['db_rows']}")

    return result


def save_ingest_report(result: dict) -> Path:
    """Persist ingest metrics as JSON evidence (SCRUM-21)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    INGEST_REPORT.write_text(
        __import__("json").dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return INGEST_REPORT


def main() -> None:
    result = ingest_to_postgres()
    report_path = save_ingest_report(result)
    print(f"Éxito: {result['rows_inserted']} registros insertados en {result['table']}.")
    if "validation" in result:
        v = result["validation"]
        print(f"Validación filas: CSV={v['expected_rows']} BD={v['db_rows']} match={v['match']}")
    print(f"Reporte: {report_path}")
