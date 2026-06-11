# Documentación de ingesta — GymPulse AI

**Sprint 1 · Equipo #31**

| | |
|---|---|
| **Repo** | https://github.com/TheYimmo/gympulse-ai-backend |
| **Jira SCRUM-8** | [US01 Ingesta](https://equipo-31-gym-pulse.atlassian.net/browse/SCRUM-8) |
| **Jira SCRUM-9** | [Calidad datos](https://equipo-31-gym-pulse.atlassian.net/browse/SCRUM-9) |
| **Jira SCRUM-11** | [Consistencia país×año](https://equipo-31-gym-pulse.atlassian.net/browse/SCRUM-11) |

---

## 1. Dataset fuente (`data/`)

| Atributo | Valor |
|----------|-------|
| Archivo | `data/clean_gym_data.csv` |
| Origen | [Kaggle — World Gym and Fitness Trends 2000–2026](https://www.kaggle.com/datasets/aryanmdev/world-gym-and-fitness-trends-20002026) |
| Registros | 3,564 |
| Países | 132 |
| Años | 2000 – 2026 |
| Regiones | 6 |
| Nulos | 0 (validado SCRUM-9) |

### Columnas (14)

`country`, `year`, `region`, `gym_memberships`, `fitness_participation_rate`, `total_health_club_revenue_usd`, `number_of_gyms`, `gym_penetration_rate`, `urban_population_percentage`, `obesity_rate`, `gdp_per_capita_usd`, `population_total`, `average_membership_cost_usd`, `insufficient_physical_activity_pct`

---

## 2. Arquitectura del pipeline

```
data/clean_gym_data.csv
       │
       ├── gympulse/ingest.py  ◄── scripts/ingest.py
       │         └──► PostgreSQL · tabla gym_metrics          SCRUM-8
       │
       ├── gympulse/quality.py ◄── scripts/quality.py
       │         └──► reports/reporte_calidad_scrum9.json     SCRUM-9
       │
       └── gympulse/consistency.py ◄── scripts/consistency.py
                 └──► reports/matriz_consistencia_scrum11.csv
                      reports/reporte_consistencia_scrum11.json  SCRUM-11

app/main.py  ──► FastAPI · /countries · /health               SCRUM-6, 10
notebooks/   ──► visualización interactiva (importan gympulse.*)
```

Todas las rutas están centralizadas en `gympulse/config.py`.

---

## 3. Instalación

```bash
python -m venv .venv && source .venv/bin/activate
make install-dev
```

| Archivo | Contenido |
|---------|-----------|
| `requirements.txt` | fastapi, uvicorn, sqlalchemy, psycopg2-binary, pandas |
| `requirements-dev.txt` | + jupyter, matplotlib, seaborn, ipykernel |

---

## 4. Ejecución paso a paso

### 4.1 API (requiere `DATABASE_URL`)

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/gympulse_db"
make api
# Swagger → http://localhost:8000/docs
```

### 4.2 Ingesta a PostgreSQL (SCRUM-8)

```bash
export DATABASE_URL="postgresql://..."
make ingest
```

> **Atención:** usa `if_exists='append'`. No re-ejecutar sin truncar `gym_metrics` o habrá duplicados.

### 4.3 Calidad de datos (SCRUM-9)

```bash
make quality
# o notebook: notebooks/02_calidad_scrum9.ipynb
```

Genera `reports/reporte_calidad_scrum9.json` con:
- Nulos globales y por región
- Atípicos IQR por región y métrica
- Estadísticas descriptivas

### 4.4 Consistencia país×año (SCRUM-11)

```bash
make consistency
# o notebook: notebooks/03_consistencia_scrum11.ipynb
```

Genera:
- `reports/matriz_consistencia_scrum11.csv` — matriz 132×27
- `reports/reporte_consistencia_scrum11.json` — resumen + `integrity_status`

### 4.5 Pipeline completo (sin BD)

```bash
make pipeline    # quality + consistency sobre CSV local
```

---

## 5. Resultados actuales (SCRUM-11)

| Métrica | Valor |
|---------|-------|
| Celdas esperadas (país×año) | 3,564 |
| Celdas con exactamente 1 registro | 3,564 |
| Cobertura | **100%** |
| Huecos | 0 |
| Duplicados | 0 |
| **integrity_status** | **PASS** |

---

## 6. Esquema PostgreSQL (`app/models.py`)

Tabla `gym_metrics`:
- PK: `id` (autoincremental)
- Dimensiones: `country`, `year`, `region`
- 11 columnas numéricas del CSV

La ingesta inserta las 14 columnas del CSV; PostgreSQL genera `id`.

---

## 7. Validación PO (SCRUM-11)

**Revisor:** Carlos Pano Hernández

| # | Criterio | Evidencia | Estado |
|---|----------|-----------|--------|
| 1 | Matriz país×año | `reports/matriz_consistencia_scrum11.csv` | ✓ |
| 2 | README ingesta | Este documento | ✓ |
| 3 | PO aprueba reporte | Comentario en [SCRUM-11](https://equipo-31-gym-pulse.atlassian.net/browse/SCRUM-11) | Pendiente |

### Checklist PO

- [ ] Revisar `reports/reporte_consistencia_scrum11.json` → `integrity_status: PASS`
- [ ] Confirmar 132 países, años 2000–2026
- [ ] Cruzar con `reports/reporte_calidad_scrum9.json` (0 nulos)
- [ ] Aprobar en Jira → mover SCRUM-11 a **Done**

---

## 8. Dependencias entre issues

```
SCRUM-6, 7 ──► SCRUM-8 ──► SCRUM-9 ──► SCRUM-11 ──► Sprint 2 (SCRUM-30, 31)
                      └──► SCRUM-10
```

SCRUM-11 está *blocked by* SCRUM-8 y SCRUM-9 en Jira; el reporte de consistencia puede generarse desde el CSV local de forma independiente.

---

*Última actualización: jun 2026 · Equipo #31*
