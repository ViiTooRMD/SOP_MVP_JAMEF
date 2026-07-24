from pathlib import Path

import pandas as pd
import pytest

from app.services.data_loader import (
    DataFileNotFoundError,
    combine_partitioned_frames,
    load_parquet,
)


def test_missing_parquet_has_clear_error(tmp_path: Path):
    with pytest.raises(DataFileNotFoundError):
        load_parquet(tmp_path / "inexistente.parquet")


def test_combine_partitioned_frames_preserves_rows_and_column_order():
    first = pd.DataFrame({"DATA": ["2026-08-01"], "FRETE": [10.0]})
    second = pd.DataFrame({"FRETE": [20.0], "DATA": ["2026-08-02"]})
    third = pd.DataFrame({"DATA": ["2026-08-03"], "FRETE": [30.0]})

    result = combine_partitioned_frames([first, second, third])

    assert result.columns.tolist() == ["DATA", "FRETE"]
    assert result["FRETE"].tolist() == [10.0, 20.0, 30.0]


def test_combine_partitioned_frames_rejects_different_schema():
    first = pd.DataFrame({"DATA": ["2026-08-01"], "FRETE": [10.0]})
    second = pd.DataFrame({"DATA": ["2026-08-02"], "PESO": [20.0]})

    with pytest.raises(ValueError, match="schema diferente"):
        combine_partitioned_frames([first, second])
