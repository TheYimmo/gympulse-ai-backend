"""Gráficas de series temporales por país/región — SCRUM-38."""
import streamlit as st


def render() -> None:
    st.title("📈 Series Temporales por País")
    st.info("**SCRUM-38** — En desarrollo · Jun 23–25")
    st.markdown(
        "Gráficas de penetración, ingresos y membresías por país seleccionado, "
        "incluyendo serie histórica 2000–2026 y proyecciones a +3 años."
    )
    st.markdown("""
    **Funcionalidades (en desarrollo):**
    - Selector de país (132 países disponibles)
    - Métricas: penetración, ingresos totales, membresías
    - Serie histórica 2000–2026 + predicción 2027–2029
    - Línea punteada para diferenciar histórico de predicción
    - Integración con `/predict/penetration` y `/metrics/{country}`
    """)
