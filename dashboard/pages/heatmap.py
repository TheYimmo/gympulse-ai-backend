"""Mapa de calor global de participación fitness e ingresos — SCRUM-37 (US03)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import dashboard.api as api


@st.cache_data(ttl=300)
def _load_batch(year: int, region: str | None) -> pd.DataFrame:
    data = api.predict_batch(year=year, region=region)
    return pd.DataFrame(data["predictions"])


def render() -> None:
    st.title("🗺️ Mapa de Calor Global")
    st.caption("US03 — Tasa de penetración de gimnasios e ingresos estimados por país y región")

    col1, col2, col3 = st.columns([2, 2, 2])
    year = col1.selectbox("Año base", [2026, 2025, 2024, 2023], index=0)
    regions = ["Todos", "Latin America", "Europe", "Asia", "North America", "Africa", "Middle East", "Oceania"]
    region_sel = col2.selectbox("Región", regions, index=0)
    metric = col3.selectbox("Métrica", ["Penetración predicha", "Penetración actual", "Cambio %"], index=0)

    region_param = None if region_sel == "Todos" else region_sel

    with st.spinner("Cargando predicciones para 132 países..."):
        try:
            df = _load_batch(year, region_param)
        except Exception as exc:
            st.error(f"Error al cargar datos: {exc}")
            return

    if df.empty:
        st.warning("No hay datos para la región seleccionada.")
        return

    color_map = {
        "Penetración predicha": ("predicted_penetration_rate", "Penetración predicha"),
        "Penetración actual": ("current_penetration_rate", "Penetración actual"),
        "Cambio %": ("predicted_change_pct", "Cambio % predicho"),
    }
    color_col, color_label = color_map[metric]

    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color=color_col,
        hover_name="country",
        hover_data={
            "region": True,
            "current_penetration_rate": ":.4f",
            "predicted_penetration_rate": ":.4f",
            "predicted_change_pct": ":.2f",
            color_col: False,
        },
        color_continuous_scale="RdYlGn",
        title=f"{color_label} — Año base {year} → predicción {year + 3}",
        labels={
            "current_penetration_rate": "Penetración actual",
            "predicted_penetration_rate": "Penetración predicha",
            "predicted_change_pct": "Cambio %",
            "region": "Región",
        },
    )
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=520,
        coloraxis_colorbar={"title": color_label, "tickformat": ".2%" if "Cambio" not in metric else ".1f"},
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Países", len(df))
    k2.metric("Penetración media predicha", f"{df['predicted_penetration_rate'].mean():.2%}")
    top_country = df.loc[df["predicted_change_pct"].idxmax(), "country"]
    k3.metric("Mayor crecimiento", top_country)
    k4.metric("Cambio medio", f"{df['predicted_change_pct'].mean():.1f}%")

    st.markdown(f"### Top 10 — {year + 3}")
    top10 = (
        df.nlargest(10, "predicted_penetration_rate")[
            ["country", "region", "current_penetration_rate", "predicted_penetration_rate", "predicted_change_pct"]
        ]
        .reset_index(drop=True)
    )
    top10.index += 1
    top10.columns = ["País", "Región", "Penetración actual", "Penetración predicha", "Cambio %"]
    top10["Penetración actual"] = top10["Penetración actual"].apply(lambda x: f"{x:.3%}")
    top10["Penetración predicha"] = top10["Penetración predicha"].apply(lambda x: f"{x:.3%}")
    top10["Cambio %"] = top10["Cambio %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(top10, width="stretch")
