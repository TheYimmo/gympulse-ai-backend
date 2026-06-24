"""Gráficas de series temporales por país con proyecciones — SCRUM-38."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import dashboard.api as api


@st.cache_data(ttl=300)
def _countries() -> list[str]:
    return api.list_countries()


@st.cache_data(ttl=300)
def _history(country: str) -> dict:
    return api.predict_penetration(country, year=2023, include_history=True)


@st.cache_data(ttl=300)
def _forecasts(country: str) -> list[dict]:
    results = []
    for base_year in [2024, 2025, 2026]:
        try:
            r = api.predict_penetration(country, year=base_year, include_history=False)
            results.append({
                "year": r["predicted_year"],
                "penetration_rate": r["predicted_penetration_rate"],
            })
        except Exception:
            pass
    return results


def render() -> None:
    st.title("📈 Series Temporales por País")
    st.caption("SCRUM-38 — Tendencias históricas 2001–2026 y proyecciones XGBoost 2026–2029")

    try:
        countries = _countries()
    except Exception as exc:
        st.error(f"Error al cargar países: {exc}")
        return

    default_idx = countries.index("Mexico") if "Mexico" in countries else 0
    country = st.selectbox("Selecciona un país", countries, index=default_idx)

    with st.spinner(f"Cargando datos para {country}..."):
        try:
            data = _history(country)
            extra_forecasts = _forecasts(country)
        except Exception as exc:
            st.error(f"Error: {exc}")
            return

    history = pd.DataFrame(data.get("history", []))
    base_forecast = {
        "year": data["predicted_year"],
        "penetration_rate": data["predicted_penetration_rate"],
    }
    forecast_df = (
        pd.DataFrame([base_forecast] + extra_forecasts)
        .sort_values("year")
        .drop_duplicates("year")
        .reset_index(drop=True)
    )

    current_pen = data.get("penetration_at_base_year", 0)
    last_pred = forecast_df["penetration_rate"].iloc[-1] if not forecast_df.empty else 0
    change_pct = data.get("predicted_change_pct", 0)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Región", data.get("region", "—"))
    k2.metric("Penetración 2023", f"{current_pen:.2%}")
    k3.metric(f"Predicción {forecast_df['year'].max()}", f"{last_pred:.2%}", delta=f"{change_pct:+.1f}%")
    peak_year = history.loc[history["penetration_rate"].idxmax(), "year"] if not history.empty else "—"
    k4.metric("Año pico histórico", peak_year)

    fig = go.Figure()

    if not history.empty:
        fig.add_trace(go.Scatter(
            x=history["year"],
            y=history["penetration_rate"],
            mode="lines+markers",
            name="Histórico",
            line={"color": "#1f77b4", "width": 2},
            marker={"size": 4},
        ))

    if not forecast_df.empty:
        if not history.empty:
            bridge_x = [int(history["year"].iloc[-1]), int(forecast_df["year"].iloc[0])]
            bridge_y = [float(history["penetration_rate"].iloc[-1]), float(forecast_df["penetration_rate"].iloc[0])]
            fig.add_trace(go.Scatter(
                x=bridge_x, y=bridge_y,
                mode="lines", showlegend=False,
                line={"color": "#ff7f0e", "width": 2, "dash": "dot"},
            ))
        fig.add_trace(go.Scatter(
            x=forecast_df["year"],
            y=forecast_df["penetration_rate"],
            mode="lines+markers",
            name="Predicción XGBoost",
            line={"color": "#ff7f0e", "width": 2, "dash": "dash"},
            marker={"size": 9, "symbol": "diamond"},
        ))

    fig.add_vline(x=2023, line_dash="dot", line_color="gray", opacity=0.4, annotation_text="Corte datos")
    fig.update_layout(
        title=f"Tasa de penetración de gimnasios — {country}",
        xaxis_title="Año",
        yaxis_title="Tasa de penetración",
        yaxis_tickformat=".2%",
        hovermode="x unified",
        height=460,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    st.plotly_chart(fig, width="stretch")

    if not history.empty:
        with st.expander("Ver datos históricos completos"):
            display = history.copy()
            display["penetration_rate"] = display["penetration_rate"].apply(lambda x: f"{x:.4%}")
            st.dataframe(
                display.rename(columns={"year": "Año", "penetration_rate": "Penetración"}),
                width="stretch",
                hide_index=True,
            )

    if not forecast_df.empty:
        with st.expander("Ver proyecciones"):
            disp = forecast_df.copy()
            disp["penetration_rate"] = disp["penetration_rate"].apply(lambda x: f"{x:.4%}")
            st.dataframe(
                disp.rename(columns={"year": "Año objetivo", "penetration_rate": "Penetración predicha"}),
                width="stretch",
                hide_index=True,
            )
