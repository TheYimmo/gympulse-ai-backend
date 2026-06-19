"""SCRUM-34 — Endpoint GET /predict/penetration con filtros país e histórico."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.ml import get_model
from gympulse.model import predict_country

router = APIRouter(prefix="/predict", tags=["Predicciones ML"])


@router.get(
    "/penetration",
    summary="Predicción de tasa de penetración a 3 años por país",
    response_description="Predicción y serie histórica del país solicitado",
)
def predict_penetration(
    country: str = Query(..., description="Nombre exacto del país (ej. 'Mexico', 'Germany')"),
    year: int = Query(2023, ge=2001, le=2026, description="Año base para la predicción (2001-2026)"),
    include_history: bool = Query(True, description="Incluir serie histórica de penetración"),
):
    """
    Predice la tasa de penetración de gimnasios **3 años** después del año base.

    - **country**: nombre del país tal como aparece en el dataset (sensible a mayúsculas).
    - **year**: año base; la predicción corresponde a `year + 3`.
    - **include_history**: si `true`, devuelve la serie histórica completa del país.
    """
    model, df_raw, region_codes = get_model()

    available = sorted(df_raw["country"].unique().tolist())
    if country not in available:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"País '{country}' no encontrado en el dataset.",
                "hint": "Consulta /predict/countries para ver los nombres exactos.",
            },
        )

    country_df = df_raw[df_raw["country"] == country]
    available_years = sorted(country_df["year"].unique().tolist())
    if year not in available_years:
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Año {year} no disponible para '{country}'.",
                "available_years": available_years,
            },
        )

    try:
        prediction = predict_country(model, df_raw, country, year, region_codes)[0]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    response = {
        "country": country,
        "region": country_df.iloc[0]["region"],
        "base_year": year,
        "predicted_year": year + 3,
        "predicted_penetration_rate": prediction["predicted_penetration_rate"],
        "model": "XGBoost",
        "horizon_years": 3,
    }

    if include_history:
        history = (
            country_df[["year", "gym_penetration_rate"]]
            .sort_values("year")
            .rename(columns={"gym_penetration_rate": "penetration_rate"})
            .to_dict("records")
        )
        current_pen = float(country_df[country_df["year"] == year].iloc[0]["gym_penetration_rate"])
        response["history"] = history
        response["penetration_at_base_year"] = current_pen
        response["predicted_change_pct"] = round(
            (prediction["predicted_penetration_rate"] - current_pen) / current_pen * 100, 2
        )

    return response


@router.get(
    "/countries",
    summary="Lista de países disponibles para predicción",
)
def list_countries():
    """Devuelve la lista de los 132 países disponibles en el dataset."""
    _, df_raw, _ = get_model()
    countries = sorted(df_raw["country"].unique().tolist())
    return {"total": len(countries), "countries": countries}


@router.get(
    "/penetration/batch",
    summary="Predicciones para múltiples países en un año base",
)
def predict_batch(
    year: int = Query(2023, ge=2001, le=2026, description="Año base para todas las predicciones"),
    region: Optional[str] = Query(None, description="Filtrar por región (opcional)"),
    top_n: Optional[int] = Query(None, ge=1, le=132, description="Devolver solo los N países con mayor penetración predicha"),
):
    """
    Genera predicciones para todos los países (o una región) en un año base.
    Útil para comparar mercados y priorizar expansión.
    """
    model, df_raw, region_codes = get_model()

    countries_df = df_raw[df_raw["year"] == year]
    if region:
        countries_df = countries_df[countries_df["region"].str.lower() == region.lower()]
        if countries_df.empty:
            available_regions = sorted(df_raw["region"].unique().tolist())
            raise HTTPException(
                status_code=404,
                detail={"error": f"Región '{region}' no encontrada.", "available_regions": available_regions},
            )

    results = []
    for country in sorted(countries_df["country"].unique()):
        try:
            pred = predict_country(model, df_raw, country, year, region_codes)[0]
            current_pen = float(countries_df[countries_df["country"] == country].iloc[0]["gym_penetration_rate"])
            results.append({
                "country": country,
                "region": df_raw[df_raw["country"] == country].iloc[0]["region"],
                "base_year": year,
                "predicted_year": year + 3,
                "current_penetration_rate": round(current_pen, 6),
                "predicted_penetration_rate": pred["predicted_penetration_rate"],
                "predicted_change_pct": round(
                    (pred["predicted_penetration_rate"] - current_pen) / current_pen * 100, 2
                ),
            })
        except Exception:
            continue

    results.sort(key=lambda x: x["predicted_penetration_rate"], reverse=True)
    if top_n:
        results = results[:top_n]

    return {
        "base_year": year,
        "predicted_year": year + 3,
        "region_filter": region,
        "total_countries": len(results),
        "predictions": results,
    }
