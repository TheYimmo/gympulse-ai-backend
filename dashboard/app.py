"""GymPulse AI — Dashboard ejecutivo (SCRUM-36)."""
import streamlit as st

st.set_page_config(
    page_title="GymPulse AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

import dashboard.api as api
from dashboard.pages import heatmap, home, reports, timeseries, whatif

_PAGES = {
    "🏠  Inicio": home,
    "🗺️  Mapa de Calor Global": heatmap,
    "📈  Series Temporales": timeseries,
    "🔬  Simulador What-If": whatif,
    "📊  Reportes Ejecutivos": reports,
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💪 GymPulse AI")
    st.caption("Dashboard ejecutivo · Equipo 31")
    st.divider()

    page_name = st.radio("Navegación", list(_PAGES.keys()), label_visibility="collapsed")

    st.divider()
    try:
        h = api.health()
        st.success(f"API ● {h.get('status', 'ok').upper()}")
        st.caption(f"DB: {h.get('database', 'unknown')}")
    except Exception:
        st.error("API ● OFFLINE")
        st.caption("Inicia FastAPI con `make api`")

    st.divider()
    st.caption("FastAPI · XGBoost · 132 países · 2000–2029")

# ── Render page ───────────────────────────────────────────────────────────────
_PAGES[page_name].render()
