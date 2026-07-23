from pathlib import Path

import pandas as pd


class DataFileNotFoundError(FileNotFoundError):
    """Raised when a required local input base is unavailable."""


def load_parquet(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise DataFileNotFoundError(f"Base não encontrada: {source}")
    return pd.read_parquet(source)


def available_columns(frame: pd.DataFrame) -> list[str]:
    return frame.columns.astype(str).tolist()
