"""Simulador económico What-If (PIB y obesidad) — SCRUM-39 (US04)."""
from __future__ import annotations

import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import dashboard.api as api


@st.cache_data(ttl=300)
def _countries() -> list[str]:
    return api.list_countries()


def render() -> None:
    st.title("🔬 Simulador Económico What-If")
    st.caption("US04 — Simula el impacto de cambios en PIB y obesidad sobre la penetración proyectada")

    try:
        countries = _countries()
    except Exception as exc:
        st.error(f"Error al cargar países: {exc}")
        return

    col1, col2 = st.columns(2)
    default_idx = countries.index("Mexico") if "Mexico" in countries else 0
    country = col1.selectbox("País", countries, index=default_idx)
    year = col2.selectbox("Año base", list(range(2026, 2000, -1)), index=0)

    st.divider()
    st.markdown("### Parámetros del escenario")
    s1, s2 = st.columns(2)
    gdp_delta = s1.slider(
        "Cambio en PIB per cápita (%)",
        min_value=-50, max_value=100, value=0, step=5,
        help="Porcentaje de variación respecto al valor actual del país seleccionado",
    )
    obesity_delta = s2.slider(
        "Cambio en tasa de obesidad (%)",
        min_value=-30, max_value=50, value=0, step=5,
        help="Porcentaje de variación en la tasa de obesidad del país",
    )

    with st.spinner("Calculando escenarios con el modelo XGBoost..."):
        try:
            result = api.predict_whatif(country, year, float(gdp_delta), float(obesity_delta))
        except Exception as exc:
            st.error(f"Error al calcular: {exc}")
            return

    base = result["scenarios"]["base"]
    whatif = result["scenarios"]["whatif"]
    impact = result["impact"]

    st.divider()
    st.markdown(f"### Resultados — **{country}** · {year} → {result['predicted_year']}")

    k1, k2, k3 = st.columns(3)
    k1.metric("Penetración base (predicha)", f"{base['predicted_penetration_rate']:.4%}")
    delta_color = impact["penetration_delta_pct"]
    k2.metric(
        "Penetración What-If (predicha)",
        f"{whatif['predicted_penetration_rate']:.4%}",
        delta=f"{delta_color:+.2f}%",
    )
    k3.metric("Impacto absoluto", f"{impact['penetration_delta']:+.6f}")

    # Bar chart
    colors = ["#1f77b4", "#2ca02c" if whatif["predicted_penetration_rate"] >= base["predicted_penetration_rate"] else "#d62728"]
    fig = go.Figure(go.Bar(
        x=["Escenario base", "Escenario What-If"],
        y=[base["predicted_penetration_rate"], whatif["predicted_penetration_rate"]],
        marker_color=colors,
        text=[f"{v:.4%}" for v in [base["predicted_penetration_rate"], whatif["predicted_penetration_rate"]]],
        textposition="outside",
        width=0.4,
    ))
    fig.update_layout(
        title=f"Comparación de escenarios — {country} ({year} → {result['predicted_year']})",
        yaxis_title="Tasa de penetración predicha",
        yaxis_tickformat=".3%",
        height=380,
        showlegend=False,
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detail table
    st.markdown("### Detalle del escenario")
    detail = pd.DataFrame({
        "Parámetro": ["PIB per cápita (USD)", "Tasa de obesidad", "Penetración predicha"],
        "Base": [
            f"${base['gdp_per_capita_usd']:,.0f}",
            f"{base['obesity_rate']:.2%}",
            f"{base['predicted_penetration_rate']:.4%}",
        ],
        "What-If": [
            f"${whatif['gdp_per_capita_usd']:,.0f}",
            f"{whatif['obesity_rate']:.2%}",
            f"{whatif['predicted_penetration_rate']:.4%}",
        ],
        "Delta": [
            f"{gdp_delta:+d}%",
            f"{obesity_delta:+d}%",
            f"{impact['penetration_delta_pct']:+.2f}%",
        ],
    })
    st.dataframe(detail, use_container_width=True, hide_index=True)

    # CSV export
    st.divider()
    export = pd.DataFrame([{
        "country": country,
        "region": result["region"],
        "base_year": year,
        "predicted_year": result["predicted_year"],
        "gdp_delta_pct": gdp_delta,
        "obesity_delta_pct": obesity_delta,
        "gdp_base_usd": base["gdp_per_capita_usd"],
        "gdp_whatif_usd": whatif["gdp_per_capita_usd"],
        "obesity_base": base["obesity_rate"],
        "obesity_whatif": whatif["obesity_rate"],
        "penetration_base": base["predicted_penetration_rate"],
        "penetration_whatif": whatif["predicted_penetration_rate"],
        "penetration_delta": impact["penetration_delta"],
        "penetration_delta_pct": impact["penetration_delta_pct"],
    }])
    buf = io.StringIO()
    export.to_csv(buf, index=False)
    st.download_button(
        label="⬇️ Exportar escenario CSV",
        data=buf.getvalue(),
        file_name=f"whatif_{country.replace(' ', '_')}_{year}.csv",
        mime="text/csv",
    )
