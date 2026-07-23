from pathlib import Path

import streamlit as st


def load_css() -> None:
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


st.set_page_config(
    page_title="S&OP Control Tower | JAMEF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()

st.markdown(
    """
    <div class="jamef-hero">
      <span class="status-pill">MVP • Peak Season</span>
      <h2>S&OP Control Tower</h2>
      <p>Demanda projetada, passagem operacional e cenários para decisão.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Ciclo de planejamento")
col1, col2, col3, col4 = st.columns(4)
col1.metric("1. Demanda", "Baseline diário", "Base validada")
col2.metric("2. Operação", "3 etapas", "Coleta • Transbordo • Entrega")
col3.metric("3. Cenário", "Restrição B2C", "Top 100 clientes")
col4.metric("4. Decisão", "Peak Season", "MVP em evolução")

st.info(
    "Acesse **Demandas e Restrições** para carregar os Parquets e explorar o MVP. "
    "Os indicadores de pessoas, veículos e custos permanecerão sem valores até a "
    "disponibilização das bases oficiais."
)

st.subheader("Escopo desta versão")
left, right = st.columns([1.2, 1])
with left:
    st.markdown(
        """
        - **Resumo Executivo:** indicadores suportados pelo baseline.
        - **Previsão de Demanda:** análise diária e identificação de picos.
        - **Passagem Operativa:** ranking mensal por filial e etapa.
        - **Restrição B2C:** cenário por cliente com comparação ao baseline.
        """
    )
with right:
    st.warning(
        "O transbordo simulado por cliente continuará bloqueado até existir "
        "uma base granular que conecte cliente, rota, filial e etapa."
    )
