from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components.layout import (
    configure_page,
    module_card,
    page_header,
    section_title,
    status_banner,
)


configure_page("S&OP Control Tower", "📊")
page_header(
    "JAMEF • PLANEJAMENTO INTEGRADO",
    "S&OP Control Tower",
    "Da demanda projetada à reconciliação financeira em uma única jornada de decisão.",
    "MVP • PEAK SEASON",
)

status_banner(
    "Fundação ativa",
    "O baseline diário e a passagem operacional habilitam as duas primeiras visões. "
    "Pessoas, veículos e custos permanecem dependentes das bases oficiais.",
    "success",
)

section_title(
    "Fluxo do planejamento",
    "Cinco módulos conectados — cada saída alimenta a próxima decisão",
)
columns = st.columns(5)
modules = [
    (
        "01",
        "Resumo Executivo",
        "Consolida demanda, capacidade e impacto financeiro.",
        "MVP PARCIAL",
        "red",
    ),
    (
        "02",
        "Demandas e Restrições",
        "Analisa o forecast e simula restrições B2C para Peak Season.",
        "MVP ATIVO",
        "blue",
    ),
    (
        "03",
        "Pessoas",
        "Traduz demanda operacional em FTE, HE e terceiros.",
        "BASE PENDENTE",
        "green",
    ),
    (
        "04",
        "Veículos",
        "Dimensiona frota e necessidade adicional por filial.",
        "BASE PENDENTE",
        "amber",
    ),
    (
        "05",
        "Custos",
        "Reconcilia custos incrementais e efeito no EBITDA.",
        "BASE PENDENTE",
        "purple",
    ),
]
for column, item in zip(columns, modules):
    with column:
        module_card(*item)

section_title("Prioridade desta rodada", "Módulo funcional para Peak Season")
left, right = st.columns([1.55, 1])
with left:
    with st.container(border=True):
        st.markdown("#### Demandas e Restrições")
        st.caption(
            "A página prioritária conecta o baseline cliente–dia–rota à passagem "
            "operacional e ao cenário de redução B2C."
        )
        step_a, step_b, step_c = st.columns(3)
        step_a.metric("Previsão", "4 métricas", "Frete • Peso • Volumes • CT-es")
        step_b.metric("Operação", "3 etapas", "Coleta • Transbordo • Entrega")
        step_c.metric("Simulação", "Top 100 B2C", "Restrição percentual")
        if st.button("Abrir Demandas e Restrições", type="primary"):
            st.switch_page("pages/02_Demandas_Restricoes.py")
with right:
    with st.container(border=True):
        st.markdown("#### Princípio de governança")
        st.caption("A interface só exibe indicadores sustentados por bases validadas.")
        st.markdown(
            """
            - Sem premissas fictícias de capacidade.
            - Sem custos demonstrativos tratados como oficiais.
            - Cenários identificados e comparáveis ao baseline.
            - Regras de negócio fora das páginas.
            """
        )
