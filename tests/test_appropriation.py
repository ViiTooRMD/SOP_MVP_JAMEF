import pandas as pd

from app.services.appropriation_service import (
    operational_ranking,
    resolve_operational_columns,
)


def test_operational_ranking():
    frame = pd.DataFrame(
        {
            "FILIAL": ["A", "A", "B"],
            "ETAPA": ["COLETA", "COLETA", "ENTREGA"],
            "PESO": [10, 20, 5],
        }
    )
    columns = resolve_operational_columns(frame)
    result = operational_ranking(frame, columns, "weight")
    assert result.iloc[0]["FILIAL"] == "A"
    assert result.iloc[0]["PESO"] == 30


def test_resolves_real_operational_output_columns():
    frame = pd.DataFrame(
        {
            "MES": ["2026-08"],
            "FILIAL_RESPONSAVEL": ["SAO"],
            "ETAPA_OPERACIONAL": ["COLETA"],
            "CTES_BASELINE": [1.0],
            "VOLUMES_BASELINE": [2.0],
            "PESO_BASELINE": [3.0],
            "CUBAGEM_BASELINE": [4.0],
        }
    )
    columns = resolve_operational_columns(frame)
    assert columns["ctes"] == "CTES_BASELINE"
    assert columns["volumes"] == "VOLUMES_BASELINE"
    assert columns["weight"] == "PESO_BASELINE"
    assert columns["cubage"] == "CUBAGEM_BASELINE"
