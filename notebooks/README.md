# notebooks/

Visualización interactiva del pipeline de datos. Importan módulos de `gympulse/`.

## Requisitos

```bash
make install-dev
make notebook
```

## Notebooks

| # | Archivo | Jira | Contenido |
|---|---------|------|-----------|
| 01 | `01_exploracion_dataset.ipynb` | — | Shape, regiones, barras por año, top 10 países |
| 02 | `02_calidad_scrum9.ipynb` | SCRUM-9 | Heatmap nulos, boxplot penetración, genera JSON |
| 03 | `03_consistencia_scrum11.ipynb` | SCRUM-11 | Heatmap país×año, resumen PO, genera reports |

## Convención de paths

Los notebooks detectan la raíz del repo automáticamente:

```python
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
```

Ejecutar siempre desde `notebooks/` (`make notebook`) o con el kernel apuntando a `.venv`.
