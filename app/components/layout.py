"""Shared visual shell for the JAMEF S&OP application."""

from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
ROOT = APP_DIR.parent
ASSETS_DIR = APP_DIR / "assets"


def configure_page(title: str, icon: str = "📊") -> None:
    st.set_page_config(
        page_title=f"{title} | S&OP JAMEF",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    css_path = ASSETS_DIR / "styles.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

    logo_path = ASSETS_DIR / "jamef_logo.jpg"
    if logo_path.exists():
        st.logo(str(logo_path), size="large")

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
          <div class="sidebar-mark">J</div>
          <div>
            <strong>S&OP</strong>
            <span>CONTROL TOWER</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="sidebar-foot">MVP • PEAK SEASON<br><span>Planejamento integrado</span></div>',
        unsafe_allow_html=True,
    )


def page_header(
    eyebrow: str,
    title: str,
    description: str,
    status: str = "MVP EM DESENVOLVIMENTO",
) -> None:
    st.markdown(
        f"""
        <div class="page-header">
          <div>
            <span class="eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            <p>{description}</p>
          </div>
          <span class="header-status">{status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str | None = None) -> None:
    detail = f"<span>{subtitle}</span>" if subtitle else ""
    st.markdown(
        f'<div class="section-title"><strong>{title}</strong>{detail}</div>',
        unsafe_allow_html=True,
    )


def status_banner(
    title: str,
    description: str,
    tone: str = "info",
) -> None:
    st.markdown(
        f"""
        <div class="status-banner {tone}">
          <span class="status-dot"></span>
          <div><strong>{title}</strong><p>{description}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pending_card(label: str, dependency: str, icon: str) -> None:
    st.markdown(
        f"""
        <div class="pending-card">
          <div class="kpi-icon muted">{icon}</div>
          <div>
            <span>{label}</span>
            <strong>Base pendente</strong>
            <small>{dependency}</small>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_card(
    number: str,
    title: str,
    description: str,
    status: str,
    tone: str,
) -> None:
    st.markdown(
        f"""
        <div class="module-card {tone}">
          <div class="module-top"><span>{number}</span><small>{status}</small></div>
          <strong>{title}</strong>
          <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def placeholder_panel(
    title: str,
    description: str,
    items: list[str],
    accent: str,
) -> None:
    bullets = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(
        f"""
        <div class="placeholder-panel {accent}">
          <span class="placeholder-label">ESTRUTURA PREPARADA</span>
          <h3>{title}</h3>
          <p>{description}</p>
          <ul>{bullets}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
