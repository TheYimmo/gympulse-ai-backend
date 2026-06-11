import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
SCRIPTS_DIR = ROOT_DIR / "scripts"

DEFAULT_CSV = DATA_DIR / "clean_gym_data.csv"
QUALITY_REPORT = REPORTS_DIR / "reporte_calidad_scrum9.json"
CONSISTENCY_MATRIX = REPORTS_DIR / "matriz_consistencia_scrum11.csv"
CONSISTENCY_SUMMARY = REPORTS_DIR / "reporte_consistencia_scrum11.json"

EXPECTED_YEARS = list(range(2000, 2027))


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    return url.replace("postgres://", "postgresql://", 1)
