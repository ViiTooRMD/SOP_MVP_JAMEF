from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from services.data_loader import load_input
from services.demand_service import daily_summary, prepare_baseline, totals
from utils.constants import BASELINE_FILENAME, JAMEF_RED
from utils.formatters import format_brl, format_number


ROOT = APP_DIR.parent


def load_css() -> None:
    css_path = ROOT / "app" / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


st.set_page_config(page_title="Resumo Executivo | JAMEF", page_icon="📈", layout="wide")
load_css()
st.title("Resumo Executivo")
st.caption("Consolidação da demanda projetada e preparação para capacidade e custos")

baseline = load_input(
    BASELINE_FILENAME,
    session_key="baseline_frame",
    label="Carregar baseline diário (Parquet)",
    root=ROOT,
)

if baseline is None:
    st.info(
        "Carregue o baseline acima ou disponibilize o arquivo em `data/input/` "
        "para habilitar os indicadores executivos."
    )
    labels = ["Frete projetado", "Peso projetado", "Volumes projetados", "CT-es projetados"]
    for column, label in zip(st.columns(4), labels):
        column.metric(label, "—")
else:
    try:
        data, columns = prepare_baseline(baseline)
        values = totals(data, columns)
        cards = [
            ("Frete projetado", format_brl(values.get("freight", 0))),
            ("Peso projetado", format_number(values.get("weight", 0))),
            ("Volumes projetados", format_number(values.get("volumes", 0))),
            ("CT-es projetados", format_number(values.get("ctes", 0))),
        ]
        for column, (label, value) in zip(st.columns(4), cards):
            column.metric(label, value)

        if "freight" in columns:
            daily = daily_summary(data, columns)
            chart = px.area(
                daily,
                x=columns["date"],
                y=columns["freight"],
                title="Receita projetada por dia",
                labels={columns["date"]: "Data", columns["freight"]: "Frete"},
                color_discrete_sequence=[JAMEF_RED],
            )
            chart.update_layout(
                height=390,
                margin=dict(l=10, r=10, t=55, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            st.plotly_chart(chart, width="stretch")
    except ValueError as error:
        st.error(str(error))

st.subheader("Próximas integrações")
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("FTE necessário", "Base pendente")
col_b.metric("Horas extras", "Base pendente")
col_c.metric("Terceiros", "Base pendente")
col_d.metric("Custo incremental", "Base pendente")

st.markdown(
    """
    **Governança do MVP:** capacidade e custos não serão preenchidos com premissas
    fictícias. Os blocos acima existem para validar a arquitetura da visão executiva
    e serão ativados somente com bases oficiais.
    """
)
