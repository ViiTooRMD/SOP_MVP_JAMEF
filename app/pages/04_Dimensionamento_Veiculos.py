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


configure_page("Dimensionamento de Veículos", "🚚")
page_header(
    "04 • FROTA E CAPACIDADE",
    "Dimensionamento de Veículos",
    "Tradução da demanda em viagens, capacidade requerida e necessidade de frota por filial.",
    "ESTRUTURA PREPARADA",
)
status_banner(
    "Base de veículos ainda não conectada",
    "O módulo será ativado quando frota atual, capacidade, utilização, viagens e "
    "custos estiverem reconciliados por filial e tipo de operação.",
    "warning",
)

section_title("Indicadores que serão ativados", "Sem valores demonstrativos")
items = [
    ("Frota atual", "Próprios, agregados e terceiros", "▣"),
    ("Viagens necessárias", "Demanda e drop size", "⇄"),
    ("Gap de veículos", "Atual versus necessário", "🚚"),
    ("Custo incremental", "Veículo próprio ou terceiro", "R$"),
]
for column, item in zip(st.columns(4), items):
    with column:
        pending_card(*item)

section_title("Arquitetura da página", "Visões previstas no contrato de dados")
left, center, right = st.columns(3)
with left:
    placeholder_panel(
        "Drop size por veículo",
        "Conversão de peso e cubagem em viagens necessárias.",
        ["VUC e Toco", "Truck e Carreta", "Capacidade por viagem"],
        "amber",
    )
with center:
    placeholder_panel(
        "Demanda × capacidade",
        "Comparação por tipo de veículo e operação.",
        ["Coleta", "Entrega", "Déficit ou excedente"],
        "amber",
    )
with right:
    placeholder_panel(
        "Frota sugerida",
        "Plano de cobertura e custo por alternativa.",
        ["Frota atual", "Necessidade adicional", "Custo unitário e total"],
        "amber",
    )

with st.expander("Campos necessários para ativar este módulo"):
    st.code(
        "MÊS | FILIAL | TIPO_OPERACAO | TIPO_VEICULO | VEICULOS_ATUAIS | "
        "CAPACIDADE_PESO | CAPACIDADE_CUBAGEM | VIAGENS_DIA | "
        "UTILIZACAO_MEDIA | CUSTO_VEICULO | CUSTO_TERCEIRO",
        language=None,
    )
