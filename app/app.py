from pathlib import Path

import streamlit as st


def load_css() -> None:
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="S&OP MVP JAMEF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()

st.title("S&OP MVP JAMEF")
st.caption("Planejamento operacional, cenários e decisão")

st.info(
    "Fundação concluída. Use o menu lateral para acessar as cinco páginas. "
    "A carga e a validação das bases serão habilitadas após a inclusão dos arquivos Parquet."
)

st.subheader("Prioridade do MVP")
st.write("A página **Demandas e Restrições** será o principal instrumento para análise de Peak Season e simulação B2C.")
