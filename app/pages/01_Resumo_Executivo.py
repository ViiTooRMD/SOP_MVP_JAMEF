from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components.charts import style_chart
from components.layout import (
    configure_page,
    page_header,
    pending_card,
    section_title,
    status_banner,
)
from services.data_loader import load_input
from services.demand_service import daily_summary, prepare_baseline, totals
from utils.constants import BASELINE_FILENAME, JAMEF_RED
from utils.formatters import format_brl, format_number


ROOT = APP_DIR.parent
configure_page("Resumo Executivo", "📈")
page_header(
    "01 • CONSOLIDAÇÃO EXECUTIVA",
    "Resumo Executivo",
    "Leitura integrada da demanda projetada e preparação das decisões de capacidade e custo.",
    "MVP PARCIAL",
)

baseline_raw = load_input(
    BASELINE_FILENAME,
    session_key="baseline_frame",
    label="Carregar baseline diário (Parquet)",
    root=ROOT,
)

if baseline_raw is None:
    status_banner(
        "Baseline não carregado",
        "Carregue o Parquet acima ou disponibilize-o em data/input para habilitar "
        "os indicadores executivos.",
        "warning",
    )
    section_title("Demanda projetada", "Indicadores aguardando o baseline")
    for column, label in zip(
        st.columns(4),
        ["Frete projetado", "Peso projetado", "Volumes projetados", "CT-es projetados"],
    ):
        column.metric(label, "—")
else:
    try:
        baseline, columns = prepare_baseline(baseline_raw)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    date_column = columns["date"]
    months = sorted(
        baseline[date_column].dt.to_period("M").astype(str).unique().tolist()
    )
    filter_a, filter_b, filter_c, filter_d = st.columns([1, 1, 1, 1.25])
    selected_months = filter_a.multiselect(
        "Período",
        months,
        default=months,
        placeholder="Selecione os meses",
    )
    view_mode = filter_b.selectbox("Visão", ["Mensal", "Diária"])
    filter_c.selectbox("Cenário", ["Baseline projetado"], disabled=True)
    filter_d.caption(
        f"Data-base: {baseline[date_column].max():%d/%m/%Y}\n\n"
        f"{len(baseline):,.0f} registros carregados"
    )

    selected = baseline
    if selected_months:
        mask = (
            baseline[date_column]
            .dt.to_period("M")
            .astype(str)
            .isin(selected_months)
        )
        selected = baseline.loc[mask]

    values = totals(selected, columns)
    section_title("Demanda projetada", "Consolidado do período selecionado")
    cards = [
        ("Frete projetado", format_brl(values.get("freight", 0))),
        ("Peso projetado", format_number(values.get("weight", 0))),
        ("Volumes projetados", format_number(values.get("volumes", 0))),
        ("CT-es projetados", format_number(values.get("ctes", 0))),
    ]
    for column, (label, value) in zip(st.columns(4), cards):
        column.metric(label, value)

    section_title("Evolução da demanda", "Alterne entre leitura mensal e diária")
    chart_column, context_column = st.columns([2.15, 1])
    with chart_column:
        with st.container(border=True):
            daily = daily_summary(selected, columns)
            freight_column = columns.get("freight")
            if freight_column:
                if view_mode == "Mensal":
                    chart_data = (
                        daily.assign(
                            PERIODO=daily[date_column].dt.to_period("M").dt.to_timestamp()
                        )
                        .groupby("PERIODO", as_index=False)[freight_column]
                        .sum()
                    )
                    x_column = "PERIODO"
                    title = "Frete projetado por mês"
                else:
                    chart_data = daily
                    x_column = date_column
                    title = "Frete projetado por dia"
                figure = px.area(
                    chart_data,
                    x=x_column,
                    y=freight_column,
                    markers=True,
                    title=title,
                    labels={x_column: "Período", freight_column: "Frete"},
                    color_discrete_sequence=[JAMEF_RED],
                )
                figure.update_traces(line=dict(width=2.6), fillcolor="rgba(200,16,46,.10)")
                st.plotly_chart(style_chart(figure, 330), width="stretch")

    with context_column:
        with st.container(border=True):
            st.markdown("#### Leitura do período")
            if not daily.empty and freight_column:
                peak = daily.loc[daily[freight_column].idxmax()]
                average = float(daily[freight_column].mean())
                st.metric("Pico diário de frete", format_brl(float(peak[freight_column])))
                st.caption(f"Ocorrido em {peak[date_column]:%d/%m/%Y}")
                st.metric("Média diária", format_brl(average))
                st.caption(f"{daily[date_column].nunique()} dias projetados")

section_title(
    "Capacidade e impacto financeiro",
    "Blocos preparados; ativação condicionada às bases oficiais",
)
pending = [
    ("MAPE do modelo", "Backtest consolidado", "↗"),
    ("FTE necessário", "Capacidade de pessoas", "👤"),
    ("Horas extras", "Capacidade de pessoas", "◷"),
    ("Terceiros", "Capacidade de pessoas", "👥"),
    ("Custo incremental", "Custos operacionais", "R$"),
]
for column, item in zip(st.columns(5), pending):
    with column:
        pending_card(*item)

st.caption(
    "Governança do MVP: nenhum indicador de capacidade ou custo é preenchido com "
    "premissas fictícias."
)
