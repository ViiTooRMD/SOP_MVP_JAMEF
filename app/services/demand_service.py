from __future__ import annotations

import re
import unicodedata

import pandas as pd


CANDIDATES = {
    "date": ["DATA", "DATA_EMISSAO", "DT_EMISSAO", "DATA_REFERENCIA", "DIA"],
    "month": ["MES", "MES_ANO", "ANO_MES", "COMPETENCIA"],
    "client_id": ["CLIENTE_GRUPO", "CNPJ_CPF", "ID_CLIENTE", "CLIENTE", "COD_CLIENTE"],
    "client_name": ["NOME", "NOME_CLIENTE", "CLIENTE_NOME", "MESTRE_GRUPO"],
    "route": ["ROTA", "ROTA_RESP", "ROTA_AJUSTADA"],
    "branch": ["FILIAL", "FILIAL_RESPONSAVEL", "FILIAL_ORIGEM", "SIGLA_ORIGEM"],
    "operation": ["OPER_B2B_B2C", "TIPO_OPERACAO", "OPERACAO", "B2B_B2C"],
    "freight": ["FRETE", "FRETE_PROJETADO", "RECEITA", "RECEITA_PROJETADA"],
    "weight": ["PESO", "PESO_PROJETADO", "PESO_CUBADO"],
    "volumes": ["QTD_VOLUMES", "VOLUMES", "VOLUME", "VOLUMES_PROJETADOS"],
    "ctes": ["QTD_CTRC", "QTD_CTES", "CTES", "CTE", "CTRC"],
    "cubage": ["CUBAGEM", "CUBAGEM_PROJETADA", "M3"],
}


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def resolve_columns(frame: pd.DataFrame) -> dict[str, str]:
    normalised = {_normalise(column): str(column) for column in frame.columns}
    resolved: dict[str, str] = {}
    for semantic, candidates in CANDIDATES.items():
        for candidate in candidates:
            if _normalise(candidate) in normalised:
                resolved[semantic] = normalised[_normalise(candidate)]
                break
    return resolved


def prepare_baseline(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    data = frame.copy()
    columns = resolve_columns(data)
    if "date" not in columns:
        raise ValueError("A base não possui uma coluna de data reconhecida.")

    data[columns["date"]] = pd.to_datetime(data[columns["date"]], errors="coerce")
    data = data.loc[data[columns["date"]].notna()].copy()
    for semantic in ("freight", "weight", "volumes", "ctes", "cubage"):
        column = columns.get(semantic)
        if column:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    return data, columns


def apply_filters(
    frame: pd.DataFrame,
    columns: dict[str, str],
    selections: dict[str, list[str]],
) -> pd.DataFrame:
    result = frame
    for semantic, selected in selections.items():
        column = columns.get(semantic)
        if column and selected:
            result = result.loc[result[column].astype(str).isin(selected)]
    return result


def daily_summary(frame: pd.DataFrame, columns: dict[str, str]) -> pd.DataFrame:
    date_column = columns["date"]
    metrics = [
        columns[name]
        for name in ("freight", "weight", "volumes", "ctes")
        if name in columns
    ]
    return (
        frame.groupby(date_column, as_index=False)[metrics]
        .sum()
        .sort_values(date_column)
    )


def totals(frame: pd.DataFrame, columns: dict[str, str]) -> dict[str, float]:
    return {
        semantic: float(frame[column].sum())
        for semantic, column in columns.items()
        if semantic in {"freight", "weight", "volumes", "ctes", "cubage"}
    }
