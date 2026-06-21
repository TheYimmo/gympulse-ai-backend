"""Página de inicio — resumen ejecutivo del dashboard (SCRUM-36)."""
import streamlit as st

import dashboard.api as api


def render() -> None:
    st.title("GymPulse AI — Dashboard Ejecutivo")
    st.markdown(
        "Plataforma de análisis predictivo para el mercado global de gimnasios. "
        "**132 países · 2000–2026 · Proyecciones a 2029** con modelo XGBoost."
    )
    st.divider()

    col1, col2, col3 = st.columns(3)
    try:
        countries = api.list_countries()
        col1.metric("Países disponibles", len(countries))
    except Exception:
        col1.metric("Países disponibles", "—")
    col2.metric("Horizonte de predicción", "3 años")
    col3.metric("Dataset", "2000 – 2026")

    st.divider()
    st.markdown("### Módulos del dashboard")

    a, b, c = st.columns(3)
    a.info("**🗺️ Mapa de Calor Global**\n\nVisualiza penetración e ingresos por país y región en un choropleth interactivo.")
    b.info("**📈 Series Temporales**\n\nExplora tendencias históricas y proyecciones 2027–2029 por país.")
    c.info("**🔬 Simulador What-If**\n\nSimula cambios en PIB u obesidad y su impacto en la penetración proyectada.")

    st.divider()
    st.markdown("### Estado de la API")
    try:
        h = api.health()
        st.json(h)
    except Exception as exc:
        st.error(f"No se puede conectar a la API: {exc}")
        st.code("make api   # inicia el servidor FastAPI en :8000")
