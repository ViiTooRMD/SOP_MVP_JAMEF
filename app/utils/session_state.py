def initialize_scenario_state():
    import streamlit as st

    st.session_state.setdefault("scenarios", [])
    st.session_state.setdefault("active_scenario", None)
