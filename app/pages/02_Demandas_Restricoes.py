from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from services.appropriation_service import operational_ranking, resolve_operational_columns
from services.data_loader import load_input
from services.demand_service import apply_filters, daily_summary, prepare_baseline, totals
from services.restriction_service import b2c_clients, simulate_restrictions
from utils.constants import APPROPRIATION_FILENAME, BASELINE_FILENAME, JAMEF_RED
from utils.formatters import format_brl, format_number


ROOT = APP_DIR.parent
METRIC_LABELS = {
    "freight": "Frete",
    "weight": "Peso",
    "volumes": "Volumes",
    "ctes": "CT-es",
    "cubage": "Cubagem",
}


def load_css() -> None:
    css_path = ROOT / "app" / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def options(frame: pd.DataFrame, column: str | None) -> list[str]:
    if not column:
        return []
    return sorted(frame[column].dropna().astype(str).unique().tolist())


def metric_cards(values: dict[str, float]) -> None:
    cards = [
        ("Frete", format_brl(values.get("freight", 0))),
        ("Peso", format_number(values.get("weight", 0))),
        ("Volumes", format_number(values.get("volumes", 0))),
        ("CT-es", format_number(values.get("ctes", 0))),
    ]
    for column, (label, value) in zip(st.columns(4), cards):
        column.metric(label, value)


st.set_page_config(
    page_title="Demandas e Restrições | JAMEF",
    page_icon="🎯",
    layout="wide",
)
load_css()
st.title("Demandas e Restrições")
st.caption("Visão operacional do Peak Season e simulação de restrição B2C")

with st.expander("Bases do MVP", expanded=True):
    upload_left, upload_right = st.columns(2)
    with upload_left:
        baseline_raw = load_input(
            BASELINE_FILENAME,
            session_key="baseline_frame",
            label="Baseline diário cliente–rota",
            root=ROOT,
        )
    with upload_right:
        appropriation_raw = load_input(
            APPROPRIATION_FILENAME,
            session_key="appropriation_frame",
            label="Passagem operacional filial–etapa",
            root=ROOT,
        )

if baseline_raw is None:
    st.info(
        "Carregue o baseline diário para liberar os filtros, os gráficos de demanda "
        "e o simulador B2C. O arquivo permanece somente na sessão."
    )
    st.stop()

try:
    baseline, columns = prepare_baseline(baseline_raw)
except ValueError as error:
    st.error(str(error))
    st.stop()

st.markdown("#### Filtros da demanda")
filter_columns = st.columns(5)
date_column = columns["date"]
months = sorted(baseline[date_column].dt.to_period("M").astype(str).unique().tolist())
selected_month = filter_columns[0].selectbox("Mês", months)
month_mask = baseline[date_column].dt.to_period("M").astype(str).eq(selected_month)
month_data = baseline.loc[month_mask].copy()

selections = {
    "client_name": filter_columns[1].multiselect(
        "Cliente", options(month_data, columns.get("client_name"))
    ),
    "route": filter_columns[2].multiselect(
        "Rota", options(month_data, columns.get("route"))
    ),
    "branch": filter_columns[3].multiselect(
        "Filial", options(month_data, columns.get("branch"))
    ),
    "operation": filter_columns[4].multiselect(
        "Operação", options(month_data, columns.get("operation"))
    ),
}
filtered = apply_filters(month_data, columns, selections)

tab_demand, tab_passage, tab_b2c = st.tabs(
    ["Previsão de Demanda", "Passagem Operativa", "Restringir B2C"]
)

with tab_demand:
    metric_cards(totals(filtered, columns))
    available_metrics = [
        semantic for semantic in ("freight", "weight", "volumes", "ctes") if semantic in columns
    ]
    selected_metric = st.segmented_control(
        "Métrica",
        available_metrics,
        format_func=lambda item: METRIC_LABELS[item],
        default=available_metrics[0],
        key="demand_metric",
    )
    daily = daily_summary(filtered, columns)
    metric_column = columns[selected_metric]
    chart = px.area(
        daily,
        x=date_column,
        y=metric_column,
        markers=True,
        labels={date_column: "Data", metric_column: METRIC_LABELS[selected_metric]},
        color_discrete_sequence=[JAMEF_RED],
    )
    chart.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    chart.update_xaxes(showgrid=False)
    chart.update_yaxes(gridcolor="#eceef1")
    st.plotly_chart(chart, width="stretch")

    if not daily.empty:
        peak = daily.loc[daily[metric_column].idxmax()]
        st.success(
            f"Pico do período: **{peak[date_column]:%d/%m/%Y}** — "
            f"**{format_number(float(peak[metric_column]))}** em "
            f"{METRIC_LABELS[selected_metric].lower()}."
        )

with tab_passage:
    if appropriation_raw is None:
        st.info("Carregue a base de passagem operacional no bloco superior.")
    else:
        operational_columns = resolve_operational_columns(appropriation_raw)
        available_operational_metrics = [
            item for item in ("weight", "volumes", "ctes", "cubage")
            if item in operational_columns
        ]
        if not available_operational_metrics:
            st.error("Nenhuma métrica operacional reconhecida na base.")
        else:
            operation_metric = st.segmented_control(
                "Métrica operacional",
                available_operational_metrics,
                format_func=lambda item: METRIC_LABELS[item],
                default=available_operational_metrics[0],
                key="operation_metric",
            )
            ranking = operational_ranking(
                appropriation_raw, operational_columns, operation_metric
            )
            metric_column = operational_columns[operation_metric]
            top = ranking.head(25).sort_values(metric_column)
            color = operational_columns.get("stage")
            chart = px.bar(
                top,
                x=metric_column,
                y=operational_columns["branch"],
                color=color,
                orientation="h",
                labels={
                    metric_column: METRIC_LABELS[operation_metric],
                    operational_columns["branch"]: "Filial",
                },
                color_discrete_sequence=[JAMEF_RED, "#1D1D1B", "#9A9CA1"],
            )
            chart.update_layout(height=650, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(chart, width="stretch")
            st.dataframe(ranking, width="stretch", hide_index=True)

with tab_b2c:
    try:
        ranking = b2c_clients(filtered, columns)
    except ValueError as error:
        st.error(str(error))
    else:
        client_id = columns["client_id"]
        client_name = columns.get("client_name")
        label_lookup = {
            str(row[client_id]): (
                f"{row[client_name]} • {row[client_id]}" if client_name else str(row[client_id])
            )
            for _, row in ranking.iterrows()
        }
        selected_clients = st.multiselect(
            "Clientes B2C a restringir",
            options=list(label_lookup),
            format_func=lambda item: label_lookup[item],
        )
        restriction = st.slider(
            "Redução aplicada aos clientes selecionados",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            format="%d%%",
        )
        restrictions = {client: restriction / 100 for client in selected_clients}
        simulated = simulate_restrictions(filtered, columns, restrictions)

        baseline_values = totals(filtered, columns)
        simulated_values = {
            semantic: float(simulated[f"{column}_SIMULADO"].sum())
            for semantic, column in columns.items()
            if semantic in {"freight", "weight", "volumes", "ctes"}
            and f"{column}_SIMULADO" in simulated
        }

        st.markdown("#### Baseline × cenário simulado")
        comparison_columns = st.columns(4)
        for output, semantic in zip(
            comparison_columns, ("freight", "weight", "volumes", "ctes")
        ):
            base = baseline_values.get(semantic, 0)
            scenario = simulated_values.get(semantic, base)
            formatter = format_brl if semantic == "freight" else format_number
            output.metric(
                METRIC_LABELS[semantic],
                formatter(scenario),
                f"{(scenario / base - 1):.1%}" if base else "0,0%",
                delta_color="inverse",
            )

        st.dataframe(ranking, width="stretch", hide_index=True)
        csv = simulated.to_csv(index=False, sep=";").encode("utf-8-sig")
        st.download_button(
            "Baixar cenário simulado",
            data=csv,
            file_name=f"cenario_b2c_{selected_month}.csv",
            mime="text/csv",
            type="primary",
        )
        st.warning(
            "A coleta e a entrega podem ser reduzidas na mesma proporção do cliente. "
            "O transbordo simulado permanece bloqueado porque a base operacional atual "
            "não contém cliente, rota e dia para uma reapropriação rastreável."
        )
