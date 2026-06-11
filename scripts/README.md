# scripts/

Puntos de entrada CLI. Cada script importa la lógica desde `gympulse/` vía `_bootstrap.py`.

| Script | Comando Make | Jira | Salida |
|--------|--------------|------|--------|
| `ingest.py` | `make ingest` | SCRUM-8 | PostgreSQL `gym_metrics` |
| `quality.py` | `make quality` | SCRUM-9 | `reports/reporte_calidad_scrum9.json` |
| `consistency.py` | `make consistency` | SCRUM-11 | `reports/matriz_*.csv`, `reports/reporte_consistencia_*.json` |

## Uso

```bash
# Desde la raíz del repo
python scripts/ingest.py       # requiere DATABASE_URL
python scripts/quality.py
python scripts/consistency.py
python scripts/consistency.py --csv data/clean_gym_data.csv
```

## `_bootstrap.py`

Añade la raíz del proyecto a `sys.path` para que `import gympulse` funcione al ejecutar desde `scripts/`.
