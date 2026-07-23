from __future__ import annotations

import re
import unicodedata

import pandas as pd


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def resolve_operational_columns(frame: pd.DataFrame) -> dict[str, str]:
    lookup = {_normalise(column): str(column) for column in frame.columns}
    candidates = {
        "month": ["MES", "MES_ANO", "ANO_MES", "COMPETENCIA"],
        "branch": ["FILIAL", "FILIAL_RESPONSAVEL", "SIGLA_FILIAL"],
        "stage": ["ETAPA", "ETAPA_OPERACIONAL", "TIPO_ETAPA"],
        "weight": ["PESO", "PESO_APROPRIADO", "PESO_PROJETADO"],
        "volumes": ["QTD_VOLUMES", "VOLUMES", "VOLUME_APROPRIADO"],
        "ctes": ["QTD_CTRC", "QTD_CTES", "CTES", "CTRC"],
        "cubage": ["CUBAGEM", "CUBAGEM_APROPRIADA", "M3"],
    }
    resolved: dict[str, str] = {}
    for semantic, options in candidates.items():
        for option in options:
            if _normalise(option) in lookup:
                resolved[semantic] = lookup[_normalise(option)]
                break
    return resolved


def operational_ranking(
    frame: pd.DataFrame,
    columns: dict[str, str],
    metric: str,
) -> pd.DataFrame:
    if "branch" not in columns or metric not in columns:
        raise ValueError("Filial ou métrica não reconhecida na base operacional.")
    group_columns = [columns["branch"]]
    if "stage" in columns:
        group_columns.append(columns["stage"])
    metric_column = columns[metric]
    data = frame.copy()
    data[metric_column] = pd.to_numeric(data[metric_column], errors="coerce").fillna(0)
    return (
        data.groupby(group_columns, as_index=False)[metric_column]
        .sum()
        .sort_values(metric_column, ascending=False)
    )
