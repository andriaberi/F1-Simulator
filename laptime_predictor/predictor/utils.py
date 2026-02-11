"""
predictor/utils.py
==================
Stateless helper functions for data I/O and transformations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from laptime_predictor.config import REQUIRED_COLS, OUTLIER_QUANTILE


def load_data(source: str | pd.DataFrame) -> pd.DataFrame:
    """
    Accept either a CSV file path or a pre-loaded DataFrame.
    Always returns a fresh copy.
    """
    if isinstance(source, pd.DataFrame):
        return source.copy()
    return pd.read_csv(source)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows with missing required columns, enforce types,
    and remove extreme outlier lap times.
    """
    df = df.dropna(subset=REQUIRED_COLS).copy()
    df["LapTime"] = df["LapTime"].astype(float)
    df["TyreLife"] = df["TyreLife"].astype(int)
    df = df[df["LapTime"] < df["LapTime"].quantile(OUTLIER_QUANTILE)]
    return df.reset_index(drop=True)


def delta_to_laptime(delta: np.ndarray, best_lap: np.ndarray) -> np.ndarray:
    """Convert predicted LapDelta back to absolute lap time."""
    return delta + best_lap
