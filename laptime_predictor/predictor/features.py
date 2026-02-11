"""
Feature engineering pipeline.
All functions are pure (no side effects) and operate on DataFrames.
"""

from __future__ import annotations

import pandas as pd

from laptime_predictor.config import (
    ROLLING_WINDOW,
    FUEL_LOAD_FACTOR,
    TYRE_DEGRADE_FACTOR,
    CATEGORICAL_FEATURES,
)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all engineered columns to *df* and return it.
    Expects a cleaned DataFrame with the standard required columns present.
    """
    df = _add_normalisation(df)
    df = _add_target(df)
    df = _add_tyre_fuel(df)
    df = _add_lap_deltas(df)
    df = _add_rolling_stats(df)
    df = _add_sector_ratios(df)
    return df


def encode_categoricals(X: pd.DataFrame) -> pd.DataFrame:
    """Cast categorical columns to the 'category' dtype required by LightGBM."""
    X = X.copy()
    for col in CATEGORICAL_FEATURES:
        if col in X.columns:
            X[col] = X[col].astype("category")
    return X


# Private helpers — each adds a coherent group of features
def _add_normalisation(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise lap and sector times relative to each driver's median at each track."""
    df["DriverTrackMedian"] = df.groupby(["Driver", "Event"])["LapTime"].transform("median")
    df["LapNorm"] = df["LapTime"] / df["DriverTrackMedian"]

    for sec in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        med = df.groupby(["Driver", "Event"])[sec].transform("median")
        df[f"{sec}_DriverTrackMedian"] = med
        df[f"{sec}_Norm"] = df[sec] / med

    return df


def _add_target(df: pd.DataFrame) -> pd.DataFrame:
    """Compute BestLap and LapDelta (model target)."""
    df["BestLap"] = df.groupby(["Driver", "Event"])["LapTime"].transform("min")
    df["LapDelta"] = df["LapTime"] - df["BestLap"]
    return df


def _add_tyre_fuel(df: pd.DataFrame) -> pd.DataFrame:
    """Tyre degradation and fuel load proxy features."""
    df["StintLap"] = df.groupby(["Driver", "Event", "Compound"]).cumcount() + 1
    df["FuelProxy"] = df["StintLap"]
    df["FuelEffect"] = 1 + df["FuelProxy"] * FUEL_LOAD_FACTOR
    df["Tyre_Degrade"] = 1 + df["TyreLife"] * TYRE_DEGRADE_FACTOR
    df["TyreFuel"] = df["Tyre_Degrade"] * df["FuelEffect"]
    df["TyreFuelSq"] = (df["Tyre_Degrade"] ** 2) * df["FuelEffect"]
    return df


def _add_lap_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """Lap-to-lap change in lap time and sector times."""
    df["LapDeltaPrev"] = (
        df.groupby(["Driver", "Event", "Compound"])["LapTime"].diff().fillna(0)
    )
    for sec in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        df[f"{sec}_PrevDelta"] = (
            df.groupby(["Driver", "Event", "Compound"])[sec].diff().fillna(0)
        )
    return df


def _add_rolling_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling mean and std (window = ROLLING_WINDOW) for lap delta and sectors."""
    for col in ["LapDelta", "Sector1Time", "Sector2Time", "Sector3Time"]:
        shifted = df.groupby(["Driver", "Event", "Compound"])[col].shift(1)
        df[f"{col}_RollMean"] = shifted.rolling(ROLLING_WINDOW).mean().fillna(0)
        df[f"{col}_RollStd"] = shifted.rolling(ROLLING_WINDOW).std().fillna(0)
    return df


def _add_sector_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Each sector's share of the total lap time."""
    df["S1_Ratio"] = df["Sector1Time"] / df["LapTime"]
    df["S2_Ratio"] = df["Sector2Time"] / df["LapTime"]
    df["S3_Ratio"] = df["Sector3Time"] / df["LapTime"]
    return df
