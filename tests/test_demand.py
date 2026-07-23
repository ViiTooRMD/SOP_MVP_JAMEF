import pandas as pd

from app.services.demand_service import daily_summary, prepare_baseline, totals


def test_daily_summary_and_totals():
    frame = pd.DataFrame(
        {
            "DATA": ["2026-08-01", "2026-08-01", "2026-08-02"],
            "FRETE": [10.0, 20.0, 30.0],
            "PESO": [1.0, 2.0, 3.0],
        }
    )
    data, columns = prepare_baseline(frame)
    result = totals(data, columns)
    daily = daily_summary(data, columns)
    assert result["freight"] == 60.0
    assert len(daily) == 2


def test_resolves_real_baseline_output_columns():
    frame = pd.DataFrame(
        {
            "DATA": ["2026-08-01"],
            "CLIENTE_GRUPO": ["CLIENTE A"],
            "FILIAL_ORIGEM_RESP": ["SAO"],
            "FRETE_BASELINE": [100.0],
            "PESO_BASELINE": [200.0],
            "VOLUMES_BASELINE": [3.0],
            "QTD_CTES_BASELINE": [1.0],
            "CUBAGEM_BASELINE": [0.5],
        }
    )
    _, columns = prepare_baseline(frame)
    assert columns["freight"] == "FRETE_BASELINE"
    assert columns["weight"] == "PESO_BASELINE"
    assert columns["volumes"] == "VOLUMES_BASELINE"
    assert columns["ctes"] == "QTD_CTES_BASELINE"
    assert columns["cubage"] == "CUBAGEM_BASELINE"
    assert columns["branch"] == "FILIAL_ORIGEM_RESP"
