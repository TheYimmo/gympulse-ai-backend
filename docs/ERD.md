# ERD — gym_metrics (SCRUM-7 / SCRUM-15)

**Tabla:** `gym_metrics`  
**Granularidad:** 1 fila por **país × año**  
**Registros esperados:** 3,564 (132 países × 27 años)

## Diagrama

```
┌─────────────────────────────────────────────────────────────┐
│                      gym_metrics                            │
├─────────────────────────────────────────────────────────────┤
│ PK  id                          SERIAL                      │
│     country                     VARCHAR  (dimensión)          │
│     year                        INTEGER  (dimensión)        │
│     region                      VARCHAR  (dimensión)        │
│ UQ  (country, year)                                         │
├─────────────────────────────────────────────────────────────┤
│     gym_memberships             FLOAT                         │
│     fitness_participation_rate  FLOAT                         │
│     total_health_club_revenue_usd FLOAT                     │
│     number_of_gyms              FLOAT                         │
│     gym_penetration_rate        FLOAT                         │
│     urban_population_percentage FLOAT                         │
│     obesity_rate                FLOAT                         │
│     gdp_per_capita_usd          FLOAT                         │
│     population_total            FLOAT                         │
│     average_membership_cost_usd FLOAT                         │
│     insufficient_physical_activity_pct FLOAT                │
└─────────────────────────────────────────────────────────────┘
```

## Relaciones

Modelo desnormalizado (single table). No hay FKs — el dataset Kaggle ya consolida país, año, región y métricas en una sola entidad analítica.

## Índices

| Índice | Columna |
|--------|---------|
| PK | `id` |
| UNIQUE | `(country, year)` |
| IX | `country`, `year`, `region` |

Ver migración: [001_create_gym_metrics.sql](../app/migrations/001_create_gym_metrics.sql)
