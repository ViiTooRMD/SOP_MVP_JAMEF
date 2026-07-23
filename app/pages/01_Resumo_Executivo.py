import streamlit as st

st.set_page_config(page_title="Resumo Executivo", page_icon="📈", layout="wide")
st.title("Resumo Executivo")
st.caption("Demanda, capacidade e impacto financeiro")

st.info("Os indicadores serão habilitados somente quando suas respectivas bases forem validadas.")

labels = ["Frete projetado", "Peso projetado", "Volumes projetados", "CT-es projetados", "MAPE"]
cols = st.columns(len(labels))
for col, label in zip(cols, labels):
    col.metric(label, "Aguardando base")

st.subheader("Visões previstas")
st.write("- Receita realizada e projetada
- Alternância mensal e diária
- Headcount preliminar
- Bridge financeira estrutural")
