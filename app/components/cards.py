"""Executive KPI card components."""


def render_metric_cards(items):
    import streamlit as st

    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        column.metric(item["label"], item.get("value", "—"), item.get("delta"))
