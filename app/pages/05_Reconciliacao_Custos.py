from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from components.layout import (
    configure_page,
    page_header,
    pending_card,
    placeholder_panel,
    section_title,
    status_banner,
)


configure_page("Reconciliação de Custos", "💰")
page_header(
    "05 • FINANCEIRO E EBITDA",
    "Reconciliação de Custos",
    "Consolidação das decisões operacionais e seus efeitos em custo, receita e EBITDA.",
    "ESTRUTURA PREPARADA",
)
status_banner(
    "Base financeira ainda não conectada",
    "A bridge e a comparação de cenários só receberão valores após reconciliação "
    "dos custos de pessoas, veículos, movimentação e estrutura fixa.",
    "warning",
)

section_title("Indicadores que serão ativados", "Sem valores demonstrativos")
items = [
    ("Custo de pessoas", "FTE, HE e terceiros", "👥"),
    ("Custo de frota", "Próprios e terceiros", "🚚"),
    ("Custo incremental", "Plano versus cenário base", "↗"),
    ("Impacto no EBITDA", "Receita e estrutura de custos", "R$"),
]
for column, item in zip(st.columns(4), items):
    with column:
        pending_card(*item)

section_title("Arquitetura da página", "Visões previstas no contrato de dados")
left, center, right = st.columns(3)
with left:
    placeholder_panel(
        "Resumo financeiro",
        "Reconciliação do cenário atual com o plano recomendado.",
        ["Receita líquida", "Custos de pessoas e frota", "EBITDA e margem"],
        "purple",
    )
with center:
    placeholder_panel(
        "Bridge de EBITDA",
        "Leitura das pontes entre resultado atual e projetado.",
        ["Pessoas", "Frota", "Outros custos e receita"],
        "purple",
    )
with right:
    placeholder_panel(
        "Comparação de cenários",
        "Visão executiva para escolha entre alternativas.",
        ["Cenário base", "Otimista", "Pessimista"],
        "purple",
    )

with st.expander("Campos necessários para ativar este módulo"):
    st.code(
        "MÊS | FILIAL | TIPO_CUSTO | CUSTO_BASE | CUSTO_INCREMENTAL | "
        "CUSTO_SIMULADO | FRETE_PROJETADO | EBITDA_BASE | EBITDA_SIMULADO",
        language=None,
    )
