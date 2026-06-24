"""Reportes ejecutivos inteligentes — SCRUM-40 (US05)."""
from __future__ import annotations

import io
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import dashboard.api as api


@st.cache_data(ttl=300)
def _load_all(year: int) -> pd.DataFrame:
    data = api.predict_batch(year=year)
    return pd.DataFrame(data["predictions"])


def _generate_summary(df: pd.DataFrame, year: int) -> str:
    top5 = df.nlargest(5, "predicted_penetration_rate")
    growth5 = df.nlargest(5, "predicted_change_pct")
    avg_pred = df["predicted_penetration_rate"].mean()
    avg_curr = df["current_penetration_rate"].mean()
    total = len(df)
    leader = top5.iloc[0]
    fastest = growth5.iloc[0]
    laggard = df.nsmallest(1, "predicted_penetration_rate").iloc[0]

    return f"""### Resumen ejecutivo automatizado — GymPulse AI · {year} → {year + 3}

A partir del análisis de **{total} países** con datos históricos 2001–{year}, el modelo XGBoost proyecta que la tasa de penetración global promedio pasará de **{avg_curr:.2%}** (actual) a **{avg_pred:.2%}** en el horizonte de 3 años, representando un incremento medio de **{(avg_pred - avg_curr) / avg_curr * 100:.1f}%**.

**Liderazgo global:** {leader['country']} ({leader['region']}) lidera con una penetración predicha de **{leader['predicted_penetration_rate']:.2%}**, consolidando su posición como el mercado fitness más maduro a nivel mundial.

**Mayor dinamismo:** {fastest['country']} ({fastest['region']}) proyecta el crecimiento más acelerado con **+{fastest['predicted_change_pct']:.1f}%**, impulsado por tendencias favorables en urbanización y gasto discrecional en salud.

**Mercados emergentes:** {laggard['country']} ({laggard['region']}) representa la mayor brecha de penetración no capturada, con una tasa predicha de {laggard['predicted_penetration_rate']:.2%}, sugiriendo alto potencial de entrada para operadores early-mover.

**Recomendación estratégica:** GymPulse debe priorizar expansión en mercados con crecimiento proyectado >10% y penetración actual <5%, donde la brecha entre oferta y demanda latente representa la mayor oportunidad en el período {year}–{year + 3}.

---
*Generado automáticamente · Modelo XGBoost (R²=0.97) · {total} países · Datos 2001–{year} · {datetime.now().strftime('%d/%m/%Y %H:%M')}*"""


def _to_excel(top5_pen: pd.DataFrame, top5_growth: pd.DataFrame, df_full: pd.DataFrame, year: int) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        top5_pen.to_excel(writer, sheet_name="Top5 Penetración", index=False)
        top5_growth.to_excel(writer, sheet_name="Top5 Crecimiento", index=False)
        df_full.to_excel(writer, sheet_name="Todos los países", index=False)
    return buf.getvalue()


def _to_pdf(top5_pen: pd.DataFrame, top5_growth: pd.DataFrame, summary: str, year: int) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(31, 119, 180)
    pdf.cell(0, 12, "GymPulse AI  Reporte Ejecutivo", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Año base: {year}   Horizonte: {year + 3}   Generado: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(3)
    pdf.set_draw_color(31, 119, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    def _table(title: str, rows: pd.DataFrame, last_col: str, last_fmt) -> None:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)
        widths = [8, 55, 42, 38, 38]
        hdrs = ["#", "Pais", "Region", "Actual", last_col]
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(31, 119, 180)
        pdf.set_text_color(255, 255, 255)
        for w, h in zip(widths, hdrs):
            pdf.cell(w, 6, h, border=1, fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for i, (_, row) in enumerate(rows.iterrows(), 1):
            pdf.set_text_color(0, 0, 0)
            fill = i % 2 == 0
            pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(widths[0], 5, str(i), border=1, fill=fill)
            pdf.cell(widths[1], 5, str(row["country"])[:26], border=1, fill=fill)
            pdf.cell(widths[2], 5, str(row["region"])[:22], border=1, fill=fill)
            pdf.cell(widths[3], 5, f"{row['current_penetration_rate']:.3%}", border=1, fill=fill)
            pdf.cell(widths[4], 5, last_fmt(row), border=1, fill=fill)
            pdf.ln()
        pdf.ln(5)

    _table(
        f"Top 5 — Mayor Penetracion Predicha ({year + 3})",
        top5_pen,
        "Predicha",
        lambda r: f"{r['predicted_penetration_rate']:.3%}",
    )
    _table(
        f"Top 5 — Mayor Crecimiento Proyectado ({year} - {year + 3})",
        top5_growth,
        "Cambio %",
        lambda r: f"{r['predicted_change_pct']:+.1f}%",
    )

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Resumen Ejecutivo Automatizado", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 8)
    for line in summary.split("\n"):
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line).strip()
        if line.startswith("###"):
            pdf.set_font("Helvetica", "B", 10)
            line = line.lstrip("# ").strip()
        elif line == "---":
            pdf.ln(2)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 8)
            continue
        else:
            pdf.set_font("Helvetica", "", 8)
        if line:
            pdf.multi_cell(0, 4.5, line)

    return bytes(pdf.output())


def render() -> None:
    st.title("📊 Reportes Ejecutivos")
    st.caption("US05 — Informe Top 5 países con resumen automatizado y exportación Excel / PDF")

    year = st.selectbox("Año base", [2026, 2025, 2024, 2023], index=0)

    with st.spinner("Generando reporte para 132 países..."):
        try:
            df = _load_all(year)
        except Exception as exc:
            st.error(f"Error al cargar datos: {exc}")
            return

    top5_pen = df.nlargest(5, "predicted_penetration_rate")[
        ["country", "region", "current_penetration_rate", "predicted_penetration_rate", "predicted_change_pct"]
    ].reset_index(drop=True)
    top5_growth = df.nlargest(5, "predicted_change_pct")[
        ["country", "region", "current_penetration_rate", "predicted_penetration_rate", "predicted_change_pct"]
    ].reset_index(drop=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Países analizados", len(df))
    k2.metric("Penetración media actual", f"{df['current_penetration_rate'].mean():.2%}")
    k3.metric(f"Penetración media {year + 3}", f"{df['predicted_penetration_rate'].mean():.2%}")
    k4.metric("Líder global", df.loc[df["predicted_penetration_rate"].idxmax(), "country"])

    st.markdown(f"### 🏆 Top 5 — Mayor Penetración Predicha ({year + 3})")
    disp_pen = top5_pen.copy()
    disp_pen.index += 1
    disp_pen.columns = ["País", "Región", "Penetración actual", "Penetración predicha", "Cambio %"]
    disp_pen["Penetración actual"] = disp_pen["Penetración actual"].apply(lambda x: f"{x:.3%}")
    disp_pen["Penetración predicha"] = disp_pen["Penetración predicha"].apply(lambda x: f"{x:.3%}")
    disp_pen["Cambio %"] = disp_pen["Cambio %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(disp_pen, use_container_width=True)

    fig = px.bar(
        top5_pen,
        x="country", y="predicted_penetration_rate",
        color="region",
        text=top5_pen["predicted_penetration_rate"].apply(lambda x: f"{x:.2%}"),
        title=f"Top 5 — Penetración predicha {year + 3}",
        labels={"country": "País", "predicted_penetration_rate": "Tasa de penetración", "region": "Región"},
    )
    fig.update_layout(yaxis_tickformat=".2%", height=340, xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🚀 Top 5 — Mayor Crecimiento Proyectado")
    disp_growth = top5_growth.copy()
    disp_growth.index += 1
    disp_growth.columns = ["País", "Región", "Penetración actual", "Penetración predicha", "Cambio %"]
    disp_growth["Penetración actual"] = disp_growth["Penetración actual"].apply(lambda x: f"{x:.3%}")
    disp_growth["Penetración predicha"] = disp_growth["Penetración predicha"].apply(lambda x: f"{x:.3%}")
    disp_growth["Cambio %"] = disp_growth["Cambio %"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(disp_growth, use_container_width=True)

    st.divider()
    summary = _generate_summary(df, year)
    st.markdown(summary)

    st.divider()
    st.markdown("### Exportar")
    col_names = ["País", "Región", "Penetración actual", "Penetración predicha", "Cambio %"]
    df_export = df[["country", "region", "current_penetration_rate", "predicted_penetration_rate", "predicted_change_pct"]].copy()
    df_export.columns = col_names

    e1, e2 = st.columns(2)
    try:
        excel_bytes = _to_excel(
            disp_pen.reset_index(drop=True),
            disp_growth.reset_index(drop=True),
            df_export,
            year,
        )
        e1.download_button(
            "⬇️ Descargar Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"gympulse_reporte_{year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as exc:
        e1.warning(f"Excel no disponible: {exc}. Instala: pip install openpyxl")

    try:
        pdf_bytes = _to_pdf(top5_pen, top5_growth, summary, year)
        e2.download_button(
            "⬇️ Descargar PDF (.pdf)",
            data=pdf_bytes,
            file_name=f"gympulse_reporte_{year}.pdf",
            mime="application/pdf",
        )
    except Exception as exc:
        e2.warning(f"PDF no disponible: {exc}. Instala: pip install fpdf2")
