# data/

**Entradas** — archivos fuente del pipeline. No se generan automáticamente.

| Archivo | Filas | Descripción |
|---------|-------|-------------|
| `clean_gym_data.csv` | 3,564 | Dataset Kaggle — 132 países × 27 años (2000–2026) |

## Origen

[World Gym and Fitness Trends 2000–2026](https://www.kaggle.com/datasets/aryanmdev/world-gym-and-fitness-trends-20002026)

## Uso

```python
from gympulse.config import DEFAULT_CSV  # → data/clean_gym_data.csv
```

```bash
python scripts/quality.py      # lee este CSV
python scripts/consistency.py  # lee este CSV
python scripts/ingest.py       # carga a PostgreSQL
```

## Notas

- No commitear datasets alternativos o exports con PII.
- Si reemplazas el CSV, re-ejecuta `make pipeline` para regenerar `reports/`.
