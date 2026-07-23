from pathlib import Path

import pytest

from app.services.data_loader import DataFileNotFoundError, load_parquet


def test_missing_parquet_has_clear_error(tmp_path: Path):
    with pytest.raises(DataFileNotFoundError):
        load_parquet(tmp_path / "inexistente.parquet")
