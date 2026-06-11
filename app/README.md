# app/

API REST con FastAPI — desplegada en Render (Docker, puerto 10000).

| Archivo | Responsabilidad | Jira |
|---------|-----------------|------|
| `main.py` | Rutas `/`, `/health`, `/countries` | SCRUM-6, 10 |
| `database.py` | Engine SQLAlchemy, `ping_database()`, `init_db()` | SCRUM-6 |
| `models.py` | Modelo `GymData` → tabla `gym_metrics` | SCRUM-7 |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Metadata del proyecto |
| GET | `/health` | Ping real a PostgreSQL (`SELECT 1`) |
| GET | `/countries` | `DISTINCT country` desde `gym_metrics` |
| GET | `/docs` | OpenAPI / Swagger |

## Ejecutar

```bash
export DATABASE_URL="postgresql://..."
uvicorn main:app --reload --port 8000
# main.py en raíz re-exporta app.main:app
```

## Pendiente Sprint 1

- [ ] `GET /metrics/{country}` — series temporales (SCRUM-10)
