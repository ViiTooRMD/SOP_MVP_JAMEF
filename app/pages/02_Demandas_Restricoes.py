import streamlit as st

st.set_page_config(page_title="Demandas e Restrições", page_icon="🎯", layout="wide")
st.title("Demandas e Restrições")
st.caption("Página prioritária do MVP para Peak Season")

tab_demanda, tab_passagem, tab_b2c = st.tabs(
    ["Previsão de Demanda", "Passagem Operativa", "Restringir B2C"]
)

with tab_demanda:
    st.info("Aguardando 134_Baseline_Diario_Cliente_Rota.parquet.")
    st.write("Visões previstas: frete, peso, volumes e CT-es por dia, com identificação de picos.")

with tab_passagem:
    st.info("Aguardando 136_Base_Simulacao_Filial_Etapa.parquet.")
    st.write("Visões previstas: coleta, transbordo e entrega por filial, métrica e período.")

with tab_b2c:
    st.info("O simulador será habilitado após validação conjunta dos dois contratos de dados.")
    st.write("Escopo: Top 100 B2C, restrição percentual e comparação baseline × cenário.")
