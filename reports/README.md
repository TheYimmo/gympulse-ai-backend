# reports/

**Salidas** — artefactos generados por `scripts/` o notebooks. Regenerables en cualquier momento.

| Archivo | Generado por | Jira | Contenido |
|---------|--------------|------|-----------|
| `reporte_calidad_scrum9.json` | `scripts/quality.py` | SCRUM-9 | Nulos, atípicos IQR por región, estadísticas |
| `matriz_consistencia_scrum11.csv` | `scripts/consistency.py` | SCRUM-11 | Matriz 132 países × 27 años (1 = OK) |
| `reporte_consistencia_scrum11.json` | `scripts/consistency.py` | SCRUM-11 | Resumen PO, `integrity_status`, gaps |

## Regenerar

```bash
make pipeline
# equivalente:
make quality && make consistency
```

## Estado actual (Sprint 1)

| Métrica | Valor |
|---------|-------|
| `integrity_status` | PASS |
| Cobertura país×año | 100% |
| Nulos globales (SCRUM-9) | 0 |

Adjuntar estos archivos como evidencia en Jira SCRUM-9 y SCRUM-11.
