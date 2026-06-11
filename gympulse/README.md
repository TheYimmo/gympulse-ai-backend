# gympulse/

Librería core — lógica reutilizable importada por scripts, notebooks y tests.

| Módulo | Función principal | Jira |
|--------|-------------------|------|
| `config.py` | Rutas (`data/`, `reports/`), `DATABASE_URL`, `EXPECTED_YEARS` | — |
| `constants.py` | Nombres de columnas del dataset | SCRUM-7 |
| `ingest.py` | `load_csv()`, `ingest_to_postgres()` | SCRUM-8 |
| `quality.py` | `build_quality_report()`, atípicos IQR por región | SCRUM-9 |
| `consistency.py` | `build_consistency_report()`, matriz país×año | SCRUM-11 |

## Uso en Python

```python
from gympulse.config import DEFAULT_CSV, REPORTS_DIR
from gympulse.quality import build_quality_report, save_quality_report
from gympulse.consistency import save_consistency_report

report = build_quality_report()
save_quality_report()
save_consistency_report()
```

## Uso en notebooks

```python
import sys
from pathlib import Path
ROOT = Path.cwd().parent  # si cwd es notebooks/
sys.path.insert(0, str(ROOT))

from gympulse.config import DEFAULT_CSV
import pandas as pd
df = pd.read_csv(DEFAULT_CSV)
```
