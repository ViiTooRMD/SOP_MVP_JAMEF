from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Sequence

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


def combine_partitioned_frames(frames: Sequence[pd.DataFrame]) -> pd.DataFrame:
    """Validate equivalent schemas and combine parquet partitions."""
    if not frames:
        raise ValueError("Nenhuma parte foi informada.")

    reference_columns = frames[0].columns.astype(str).tolist()
    reference_set = set(reference_columns)
    for position, frame in enumerate(frames[1:], start=2):
        current_columns = frame.columns.astype(str).tolist()
        if set(current_columns) != reference_set:
            missing = sorted(reference_set.difference(current_columns))
            additional = sorted(set(current_columns).difference(reference_set))
            details = []
            if missing:
                details.append(f"faltando: {', '.join(missing)}")
            if additional:
                details.append(f"adicionais: {', '.join(additional)}")
            raise ValueError(
                f"A parte {position} possui schema diferente da parte 1"
                + (f" ({'; '.join(details)})" if details else ".")
            )

    aligned = [frame.reindex(columns=reference_columns) for frame in frames]
    return pd.concat(aligned, ignore_index=True, copy=False)


def load_partitioned_input(
    filename: str,
    *,
    session_key: str,
    label: str,
    root: Path,
    expected_parts: int = 3,
) -> pd.DataFrame | None:
    """Load one local baseline or consolidate a fixed number of uploaded parts."""
    source_names_key = f"{session_key}_source_names"
    if session_key in st.session_state:
        names = st.session_state.get(source_names_key, [])
        description = " • ".join(names) if names else "base consolidada"
        st.success(f"{label} carregado: {description}")
        if st.button(
            "Substituir partes do baseline",
            key=f"replace_{session_key}",
            use_container_width=True,
        ):
            st.session_state.pop(session_key, None)
            st.session_state.pop(source_names_key, None)
            st.rerun()
        return st.session_state[session_key]

    local_path = root / "data" / "input" / filename
    if local_path.exists():
        frame = load_parquet(local_path)
        st.session_state[session_key] = frame
        st.session_state[source_names_key] = [local_path.name]
        return frame

    st.markdown(f"**{label}**")
    st.caption(
        f"Selecione as {expected_parts} partes do mesmo baseline. "
        "A consolidação ocorrerá somente após todos os arquivos serem informados."
    )
    columns = st.columns(expected_parts)
    uploads = []
    for index, column in enumerate(columns, start=1):
        with column:
            uploaded = st.file_uploader(
                f"Parte {index} de {expected_parts}",
                type=["parquet"],
                key=f"upload_{session_key}_part_{index}",
            )
            if uploaded is not None:
                uploads.append(uploaded)

    st.caption(f"{len(uploads)} de {expected_parts} partes selecionadas")
    if len(uploads) != expected_parts:
        return None

    consolidate = st.button(
        f"Consolidar {expected_parts} partes",
        key=f"consolidate_{session_key}",
        type="primary",
        use_container_width=True,
    )
    if not consolidate:
        return None

    try:
        frames = [load_uploaded_parquet(uploaded.getvalue()) for uploaded in uploads]
        frame = combine_partitioned_frames(frames)
    except Exception as error:
        st.error(f"Não foi possível consolidar as partes: {error}")
        return None

    st.session_state[session_key] = frame
    st.session_state[source_names_key] = [uploaded.name for uploaded in uploads]
    return frame


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
