"""Executive KPI card components."""


def render_metric_cards(items, columns_count: int | None = None):
    import streamlit as st

    columns = st.columns(columns_count or len(items))
    for column, item in zip(columns, items):
        column.metric(
            item["label"],
            item.get("value", "—"),
            item.get("delta"),
            delta_color=item.get("delta_color", "normal"),
            help=item.get("help"),
        )
