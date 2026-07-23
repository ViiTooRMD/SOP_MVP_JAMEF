from __future__ import annotations

import pandas as pd


METRICS = ("freight", "weight", "volumes", "ctes")


def b2c_clients(
    frame: pd.DataFrame,
    columns: dict[str, str],
    *,
    top_n: int = 100,
) -> pd.DataFrame:
    operation = columns.get("operation")
    client_id = columns.get("client_id")
    if not operation or not client_id:
        raise ValueError("A base precisa conter operação B2B/B2C e identificador do cliente.")

    b2c = frame.loc[
        frame[operation].astype(str).str.upper().str.contains("B2C", na=False)
    ].copy()
    group_columns = [client_id]
    if columns.get("client_name"):
        group_columns.append(columns["client_name"])
    metric_columns = [columns[item] for item in METRICS if item in columns]
    ranking = b2c.groupby(group_columns, as_index=False)[metric_columns].sum()
    order = columns.get("freight") or metric_columns[0]
    return ranking.sort_values(order, ascending=False).head(top_n)


def simulate_restrictions(
    frame: pd.DataFrame,
    columns: dict[str, str],
    restrictions: dict[str, float],
) -> pd.DataFrame:
    """Apply reductions expressed as 0..1 to selected B2C clients."""
    client_id = columns["client_id"]
    operation = columns["operation"]
    result = frame.copy()
    rate = result[client_id].astype(str).map(restrictions).fillna(0.0).clip(0, 1)
    is_b2c = result[operation].astype(str).str.upper().str.contains("B2C", na=False)
    factor = 1 - rate.where(is_b2c, 0.0)
    for semantic in METRICS:
        column = columns.get(semantic)
        if column:
            result[f"{column}_SIMULADO"] = result[column] * factor
    return result
