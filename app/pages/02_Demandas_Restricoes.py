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
    section_title,
    status_banner,
)
from services.appropriation_service import operational_ranking, resolve_operational_columns
from services.data_loader import load_input, load_partitioned_input
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


configure_page("Demandas e Restrições", "🎯")
page_header(
    "02 • PEAK SEASON",
    "Demandas e Restrições B2C",
    "Forecast diário, passagem pelas filiais e simulação de restrições por cliente.",
    "MÓDULO PRIORITÁRIO",
)

with st.expander("Bases do MVP", expanded=True):
    baseline_raw = load_partitioned_input(
        BASELINE_FILENAME,
        session_key="baseline_frame",
        label="Baseline diário cliente–rota",
        root=ROOT,
        expected_parts=3,
    )
    st.divider()
    appropriation_raw = load_input(
        APPROPRIATION_FILENAME,
        session_key="appropriation_frame",
        label="Passagem operacional filial–etapa",
        root=ROOT,
    )

if baseline_raw is None:
    status_banner(
        "Baseline diário ainda não consolidado",
        "Carregue as três partes no bloco Bases do MVP e clique em Consolidar. "
        "As análises serão liberadas somente após a validação dos schemas.",
        "warning",
    )
    st.stop()

try:
    baseline, columns = prepare_baseline(baseline_raw)
except ValueError as error:
    st.error(str(error))
    st.stop()

date_column = columns["date"]
months = sorted(baseline[date_column].dt.to_period("M").astype(str).unique().tolist())
selected_month = st.selectbox("Mês de análise", months, label_visibility="collapsed")
month_mask = baseline[date_column].dt.to_period("M").astype(str).eq(selected_month)
month_data = baseline.loc[month_mask]

section_title("Filtros do cenário", "Aplicados aos três módulos da página")
filter_columns = st.columns(5)
selections = {
    "client_name": filter_columns[0].multiselect(
        "Cliente", options(month_data, columns.get("client_name"))
    ),
    "route": filter_columns[1].multiselect(
        "Rota", options(month_data, columns.get("route"))
    ),
    "branch": filter_columns[2].multiselect(
        "Filial", options(month_data, columns.get("branch"))
    ),
    "operation": filter_columns[3].multiselect(
        "Operação", options(month_data, columns.get("operation"))
    ),
}
filter_columns[4].selectbox(
    "Período",
    [selected_month],
    disabled=True,
    help="O MVP simula um mês por vez.",
)
filtered = apply_filters(month_data, columns, selections)

status_banner(
    "Baseline pronto para análise",
    f"{len(filtered):,.0f} registros após os filtros • "
    f"{filtered[date_column].nunique()} dias • cenário sem alteração de rotas.",
    "success",
)

active_module = st.segmented_control(
    "Módulo de análise",
    ["Previsão de Demanda", "Passagem Operativa", "Restringir B2C"],
    default="Previsão de Demanda",
    width="stretch",
)

if active_module == "Previsão de Demanda":
    section_title("Previsão de demanda", "Visão diária do período filtrado")
    metric_cards(totals(filtered, columns))
    available_metrics = [
        item for item in ("freight", "weight", "volumes", "ctes") if item in columns
    ]
    control, context = st.columns([2.2, 1])
    with control:
        selected_metric = st.segmented_control(
            "Métrica",
            available_metrics,
            format_func=lambda item: METRIC_LABELS[item],
            default=available_metrics[0],
            key="demand_metric",
        )
        daily = daily_summary(filtered, columns)
        metric_column = columns[selected_metric]
        figure = px.area(
            daily,
            x=date_column,
            y=metric_column,
            markers=True,
            title=f"{METRIC_LABELS[selected_metric]} projetado por dia",
            labels={date_column: "Data", metric_column: METRIC_LABELS[selected_metric]},
            color_discrete_sequence=[JAMEF_RED],
        )
        figure.update_traces(line=dict(width=2.5), fillcolor="rgba(200,16,46,.10)")
        with st.container(border=True):
            st.plotly_chart(style_chart(figure, 360), width="stretch")
    with context:
        with st.container(border=True):
            st.markdown("#### Pico do período")
            if not daily.empty:
                peak = daily.loc[daily[metric_column].idxmax()]
                st.metric(
                    METRIC_LABELS[selected_metric],
                    format_number(float(peak[metric_column])),
                )
                st.caption(f"{peak[date_column]:%d/%m/%Y}")
                st.markdown("#### Comparação")
                st.metric(
                    "Pico × média diária",
                    f"{(float(peak[metric_column]) / daily[metric_column].mean() - 1):.1%}",
                )
                st.caption("Intensidade acima da média do período")

elif active_module == "Passagem Operativa":
    section_title(
        "Passagem operativa",
        "Ranking mensal por filial e etapa — coleta, transbordo e entrega",
    )
    if appropriation_raw is None:
        status_banner(
            "Passagem operacional não carregada",
            "Carregue a base filial–etapa em Bases do MVP.",
            "warning",
        )
    else:
        operational_columns = resolve_operational_columns(appropriation_raw)
        available_operational_metrics = [
            item
            for item in ("weight", "volumes", "ctes", "cubage")
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
            top = ranking.head(20).sort_values(metric_column)
            chart_col, table_col = st.columns([1.25, 1])
            with chart_col:
                figure = px.bar(
                    top,
                    x=metric_column,
                    y=operational_columns["branch"],
                    color=operational_columns.get("stage"),
                    orientation="h",
                    title="Top 20 filiais",
                    labels={
                        metric_column: METRIC_LABELS[operation_metric],
                        operational_columns["branch"]: "Filial",
                    },
                    color_discrete_sequence=[JAMEF_RED, "#213B66", "#9BA6B5"],
                )
                with st.container(border=True):
                    st.plotly_chart(style_chart(figure, 510), width="stretch")
            with table_col:
                with st.container(border=True):
                    st.markdown("#### Detalhamento por filial")
                    st.dataframe(
                        ranking,
                        width="stretch",
                        height=458,
                        hide_index=True,
                    )

elif active_module == "Restringir B2C":
    section_title(
        "Simulador de restrição B2C",
        "Top 100 clientes • redução percentual • um mês por cenário",
    )
    try:
        ranking = b2c_clients(filtered, columns)
    except ValueError as error:
        st.error(str(error))
    else:
        client_id = columns["client_id"]
        client_name = columns.get("client_name")
        label_lookup = {
            str(row[client_id]): (
                f"{row[client_name]} • {row[client_id]}"
                if client_name
                else str(row[client_id])
            )
            for _, row in ranking.iterrows()
        }
        selection_col, restriction_col = st.columns([2.1, 1])
        selected_clients = selection_col.multiselect(
            "Clientes B2C a restringir",
            options=list(label_lookup),
            format_func=lambda item: label_lookup[item],
            placeholder="Selecione um ou mais clientes",
        )
        restriction = restriction_col.slider(
            "Redução aplicada",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            format="%d%%",
        )
        table_col, action_col = st.columns([2.2, 1])
        with table_col:
            with st.container(border=True):
                st.markdown("#### Ranking B2C do período")
                st.dataframe(ranking, width="stretch", height=390, hide_index=True)
        with action_col:
            with st.container(border=True):
                st.markdown("#### Cenário atual")
                st.metric("Clientes restringidos", len(selected_clients))
                st.metric("Redução aplicada", f"{restriction}%")
                st.caption(
                    "O transbordo simulado permanece bloqueado até existir uma "
                    "base granular com cliente, rota, filial e dia."
                )

        if not selected_clients:
            status_banner(
                "Selecione clientes para calcular o cenário",
                "O baseline permanece inalterado até que ao menos um cliente B2C "
                "e um percentual de redução sejam definidos.",
                "info",
            )
        else:
            restrictions = {client: restriction / 100 for client in selected_clients}
            simulated = simulate_restrictions(filtered, columns, restrictions)
            baseline_values = totals(filtered, columns)
            simulated_values = {
                semantic: float(simulated[f"{column}_SIMULADO"].sum())
                for semantic, column in columns.items()
                if semantic in {"freight", "weight", "volumes", "ctes"}
                and f"{column}_SIMULADO" in simulated
            }

            section_title(
                "Baseline × cenário",
                "Resultado após as restrições selecionadas",
            )
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

            csv_columns = [
                columns[key]
                for key in ("date", "client_id", "route", "operation")
                if key in columns
            ] + [
                column
                for column in simulated.columns
                if column.endswith("_SIMULADO")
            ]
            csv = (
                simulated[csv_columns]
                .to_csv(index=False, sep=";")
                .encode("utf-8-sig")
            )
            st.download_button(
                "Baixar cenário simulado",
                data=csv,
                file_name=f"cenario_b2c_{selected_month}.csv",
                mime="text/csv",
                type="primary",
            )
