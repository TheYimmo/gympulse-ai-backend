"""Simulador económico What-If (PIB y obesidad) — SCRUM-39."""
import streamlit as st


def render() -> None:
    st.title("🔬 Simulador Económico What-If")
    st.info("**SCRUM-39** — En desarrollo · Jun 25–28")
    st.markdown(
        "Simula cambios en PIB per cápita y tasa de obesidad para observar "
        "el impacto en la penetración proyectada de gimnasios."
    )
    st.markdown("""
    **Funcionalidades (en desarrollo):**
    - Sliders interactivos: PIB per cápita (±50 %) y tasa de obesidad (±30 %)
    - Recálculo en tiempo real vía `GET /predict/whatif`
    - Comparación visual: escenario base vs. What-If
    - Exportación del escenario en CSV
    """)
