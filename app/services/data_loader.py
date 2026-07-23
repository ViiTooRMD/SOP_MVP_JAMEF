from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


class DataFileNotFoundError(FileNotFoundError):
    """Raised when a required input base is unavailable."""


@st.cache_data(show_spinner=False)
def load_parquet(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise DataFileNotFoundError(f"Base não encontrada: {source}")
    return pd.read_parquet(source)


@st.cache_data(show_spinner="Carregando e validando a base...")
def load_uploaded_parquet(content: bytes) -> pd.DataFrame:
    return pd.read_parquet(BytesIO(content))


def load_input(
    filename: str,
    *,
    session_key: str,
    label: str,
    root: Path,
) -> pd.DataFrame | None:
    """Load a local input when available, otherwise expose a cloud uploader."""
    if session_key in st.session_state:
        return st.session_state[session_key]

    local_path = root / "data" / "input" / filename
    if local_path.exists():
        frame = load_parquet(local_path)
        st.session_state[session_key] = frame
        return frame

    uploaded = st.file_uploader(label, type=["parquet"], key=f"upload_{session_key}")
    if uploaded is None:
        return None

    frame = load_uploaded_parquet(uploaded.getvalue())
    st.session_state[session_key] = frame
    return frame


def available_columns(frame: pd.DataFrame) -> list[str]:
    return frame.columns.astype(str).tolist()
