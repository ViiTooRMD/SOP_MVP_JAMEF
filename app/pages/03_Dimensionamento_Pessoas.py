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


configure_page("Dimensionamento de Pessoas", "👥")
page_header(
    "03 • CAPACIDADE OPERACIONAL",
    "Dimensionamento de Pessoas",
    "Conversão da demanda por filial e etapa em capacidade, FTE, horas extras e terceiros.",
    "ESTRUTURA PREPARADA",
)
status_banner(
    "Base de pessoas ainda não conectada",
    "A tela apresenta o desenho funcional, mas não calcula headcount até receber "
    "produtividade, jornada, absenteísmo e custos oficiais.",
    "warning",
)

section_title("Indicadores que serão ativados", "Sem valores demonstrativos")
items = [
    ("FTE necessário", "Headcount e produtividade", "👤"),
    ("Horas extras", "Jornada e saldo disponível", "◷"),
    ("Terceiros", "Política e capacidade contratada", "👥"),
    ("Gap de capacidade", "Demanda versus horas produtivas", "↗"),
]
for column, item in zip(st.columns(4), items):
    with column:
        pending_card(*item)

section_title("Arquitetura da página", "Visões previstas no contrato de dados")
left, center, right = st.columns(3)
with left:
    placeholder_panel(
        "Capacidade × demanda",
        "Comparação diária ou mensal por filial e etapa operacional.",
        ["Demanda ajustada", "Capacidade atual", "Déficit ou excedente"],
        "green",
    )
with center:
    placeholder_panel(
        "Necessidade média de pessoas",
        "Dimensionamento por função a partir de horas produtivas.",
        ["Ajudante", "Conferente", "Produtividade por hora"],
        "green",
    )
with right:
    placeholder_panel(
        "Plano de atendimento",
        "Recomendação de alavancas conforme horizonte e intensidade.",
        ["Horas extras", "Terceiros", "Contratação perene"],
        "green",
    )

with st.expander("Campos necessários para ativar este módulo"):
    st.code(
        "MÊS | FILIAL | FUNÇÃO | ETAPA_OPERACIONAL | HEADCOUNT_ATUAL | "
        "HORAS_DISPONIVEIS | PRODUTIVIDADE_POR_HORA | ABSENTEISMO | "
        "HORAS_EXTRAS_DISPONIVEIS | TERCEIROS_ATUAIS | CUSTO_FTE | "
        "CUSTO_HORA_EXTRA | CUSTO_TERCEIRO",
        language=None,
    )
