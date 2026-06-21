"""Mapa de calor global de participación fitness e ingresos — SCRUM-37."""
import streamlit as st


def render() -> None:
    st.title("🗺️ Mapa de Calor Global")
    st.info("**SCRUM-37** — En desarrollo · Jun 22–25")
    st.markdown(
        "Mapa choropleth interactivo con tasa de penetración de gimnasios e ingresos "
        "estimados por país. Filtro por región y selector de año base."
    )
    st.markdown("""
    **Funcionalidades (en desarrollo):**
    - Choropleth Plotly Express — penetración e ingresos por país
    - Filtro por región (Europa, Asia, LATAM, Norteamérica, África, Oceanía)
    - Selector de año base 2001–2026
    - Código de colores por ingresos: alto / medio / bajo
    - Renderizado < 2 s con `@st.cache_data`
    """)
