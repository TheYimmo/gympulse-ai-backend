# GymPulse AI — Backend

**Equipo #31 · Sprint 1 · ITESM**

Plataforma de ingesta y consulta del mercado fitness global — 132 países, 2000–2026.

| | |
|---|---|
| **Repo** | https://github.com/TheYimmo/gympulse-ai-backend |
| **Jira** | https://equipo-31-gym-pulse.atlassian.net/jira/software/projects/SCRUM/boards/1 |
| **Stack** | Python 3.10 · FastAPI · PostgreSQL · pandas · Jupyter |

---

## Estructura del proyecto

```
gympulse-ai-backend/
├── app/                    # API REST (FastAPI)           → SCRUM-6, 10
│   ├── main.py             #   /, /health, /countries
│   ├── database.py
│   └── models.py           #   tabla gym_metrics          → SCRUM-7
├── gympulse/               # Librería core (importable)
│   ├── config.py           #   rutas: data/, reports/
│   ├── ingest.py           #   ETL                        → SCRUM-8
│   ├── quality.py          #   calidad + atípicos IQR     → SCRUM-9
│   └── consistency.py      #   matriz país×año            → SCRUM-11
├── data/                   # Entradas (no generadas)
│   └── clean_gym_data.csv
├── reports/                # Salidas generadas
│   ├── reporte_calidad_scrum9.json
│   ├── matriz_consistencia_scrum11.csv
│   └── reporte_consistencia_scrum11.json
├── scripts/                # CLI (ejecutables)
│   ├── ingest.py
│   ├── quality.py
│   └── consistency.py
├── notebooks/              # Visualización Jupyter
├── main.py                 # Entry uvicorn / Docker
├── Dockerfile
├── Makefile
├── requirements.txt
└── requirements-dev.txt
```

**Capas:** `gympulse/` = lógica · `scripts/` = CLI · `notebooks/` = gráficos · `app/` = API · `reports/` = artefactos

---

## Inicio rápido

```bash
git clone https://github.com/TheYimmo/gympulse-ai-backend.git
cd gympulse-ai-backend

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
make install-dev

export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
make api                           # → http://localhost:8000/docs
```

---

## Comandos (`Makefile`)

| Comando | Descripción | Jira |
|---------|-------------|------|
| `make install` | Dependencias producción | |
| `make install-dev` | + Jupyter, matplotlib, seaborn | |
| `make api` | FastAPI en puerto 8000 | SCRUM-6, 10 |
| `make ingest` | CSV → PostgreSQL | SCRUM-8 |
| `make quality` | → `reports/reporte_calidad_scrum9.json` | SCRUM-9 |
| `make consistency` | → `reports/matriz_*.csv` + JSON | SCRUM-11 |
| `make pipeline` | quality + consistency | SCRUM-9, 11 |
| `make notebook` | Jupyter en `notebooks/` | |

Sin Make:

```bash
python scripts/ingest.py
python scripts/quality.py
python scripts/consistency.py
uvicorn main:app --reload --port 8000
```

---

## API (SCRUM-10)

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Info del proyecto |
| `GET /health` | Estado + ping PostgreSQL |
| `GET /countries` | Lista de países en BD |
| `GET /docs` | Swagger UI |

**Deploy Docker** (Render, puerto 10000):

```bash
docker build -t gympulse-api .
docker run -p 10000:10000 -e DATABASE_URL="..." gympulse-api
```

---

## Notebooks

| Notebook | Contenido | Jira |
|----------|-----------|------|
| [01_exploracion_dataset.ipynb](notebooks/01_exploracion_dataset.ipynb) | EDA, regiones, top países | — |
| [02_calidad_scrum9.ipynb](notebooks/02_calidad_scrum9.ipynb) | Nulos, boxplots, JSON | SCRUM-9 |
| [03_consistencia_scrum11.ipynb](notebooks/03_consistencia_scrum11.ipynb) | Heatmap país×año, resumen PO | SCRUM-11 |

```bash
make notebook
```

---

## Documentación

| Archivo | Contenido |
|---------|-----------|
| [README_INGESTA.md](README_INGESTA.md) | Pipeline completo, criterios PO, SCRUM-11 |
| [data/README.md](data/README.md) | Dataset fuente |
| [reports/README.md](reports/README.md) | Artefactos generados |
| [scripts/README.md](scripts/README.md) | CLI y bootstrap |
| [gympulse/README.md](gympulse/README.md) | Módulos de la librería |
| [app/README.md](app/README.md) | API FastAPI |
| [notebooks/README.md](notebooks/README.md) | Guía Jupyter |

---

## Variables de entorno

| Variable | Requerida | Uso |
|----------|-----------|-----|
| `DATABASE_URL` | ingest + API | `postgresql://user:pass@host:port/db` |

---

## Equipo

| Rol | Miembro |
|-----|---------|
| Product Owner | Carlos Pano Hernández |
| Scrum Master | Yael Illair Martinez Morales |
| Developer | Mario Javier Soriano · Edgar Rosas Gómez |
