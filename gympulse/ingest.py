"""SCRUM-8 — Pipeline ETL CSV → PostgreSQL."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from gympulse.config import DEFAULT_CSV, get_database_url


def load_csv(csv_path: Path | None = None) -> pd.DataFrame:
    path = csv_path or DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {path}")
    return pd.read_csv(path)


def ingest_to_postgres(
    csv_path: Path | None = None,
    table: str = "gym_metrics",
    if_exists: str = "append",
) -> dict:
    """Carga el CSV en PostgreSQL. Retorna métricas de la operación."""
    db_url = get_database_url()
    if not db_url:
        raise RuntimeError("Define DATABASE_URL antes de ejecutar la ingesta.")

    df = load_csv(csv_path)
    source_rows = len(df)

    engine = create_engine(db_url)
    df.to_sql(table, engine, if_exists=if_exists, index=False)

    return {
        "source_file": str(csv_path or DEFAULT_CSV),
        "rows_inserted": source_rows,
        "table": table,
        "status": "ok",
    }


def main() -> None:
    result = ingest_to_postgres()
    print(f"Éxito: {result['rows_inserted']} registros insertados en {result['table']}.")
