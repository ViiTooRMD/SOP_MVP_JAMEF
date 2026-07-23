"""Reusable Plotly styling for the application."""

from typing import Any


def style_chart(figure: Any, height: int = 350, legend: str = "h") -> Any:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=34, b=12),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Segoe UI, Arial", color="#4B5565", size=11),
        title=dict(font=dict(size=13, color="#242832")),
        legend=dict(
            orientation=legend,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(bgcolor="#101F3D", font_color="white"),
    )
    figure.update_xaxes(showgrid=False, linecolor="#E3E8F0")
    figure.update_yaxes(gridcolor="#EEF1F5", zerolinecolor="#D9DFE8")
    return figure
