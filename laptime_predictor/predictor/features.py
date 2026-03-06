"""
Feature engineering pipeline.
All functions are pure (no side effects) and operate on DataFrames.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from laptime_predictor.config import (
    ROLLING_WINDOW,
    FUEL_LOAD_FACTOR,
    TYRE_DEGRADE_FACTOR,
    COMPOUND_DEGRADE_MULTIPLIER,
    COMPOUND_WARMUP_LAPS,
    COMPOUND_PEAK_LAP,
    COMPOUND_CLIFF_LAP,
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


def _compound_curve(df: pd.DataFrame, mapping: dict[str, float], default: float) -> pd.Series:
    """Map compound string to scalar curve parameter with default fallback."""
    return df["Compound"].astype(str).str.upper().map(mapping).fillna(default)


def _add_tyre_fuel(df: pd.DataFrame) -> pd.DataFrame:
    """Tyre degradation and fuel load proxy features."""
    df["StintLap"] = df.groupby(["Driver", "Event", "Compound"]).cumcount() + 1
    df["FuelProxy"] = df["StintLap"]
    df["FuelEffect"] = 1 + df["FuelProxy"] * FUEL_LOAD_FACTOR
    df["Tyre_Degrade"] = 1 + df["TyreLife"] * TYRE_DEGRADE_FACTOR
    df["RaceLap"] = df.groupby(["Driver", "Event"]).cumcount() + 1
    df["FuelProxy"] = df["RaceLap"]

    race_length = df.groupby(["Driver", "Event"])["RaceLap"].transform("max")
    df["FuelLoadStart"] = 1 + (race_length - 1) * FUEL_LOAD_FACTOR
    df["FuelBurn"] = (df["RaceLap"] - 1) * FUEL_LOAD_FACTOR
    df["FuelRemaining"] = (df["FuelLoadStart"] - df["FuelBurn"]).clip(lower=1.0)
    df["FuelEffect"] = df["FuelRemaining"]

    compound_factor = _compound_curve(df, COMPOUND_DEGRADE_MULTIPLIER, 1.0)
    warmup_lap = _compound_curve(df, COMPOUND_WARMUP_LAPS, 3.0)
    peak_lap = _compound_curve(df, COMPOUND_PEAK_LAP, 8.0)
    cliff_lap = _compound_curve(df, COMPOUND_CLIFF_LAP, 24.0)

    df["TyreLifeSq"] = df["TyreLife"] ** 2
    df["TyreLifeLog"] = np.log1p(df["TyreLife"])

    # Tyre lifecycle: start slower, hit peak grip, then degrade and eventually cliff
    warmup_progress = (df["TyreLife"] / warmup_lap).clip(0, 2)
    df["TyreWarmup"] = (1 - np.exp(-2.2 * warmup_progress)).clip(0, 1)

    peak_width = (0.35 * peak_lap).clip(lower=1.0)
    peak_dist = (df["TyreLife"] - peak_lap) / peak_width
    df["TyrePeakGrip"] = np.exp(-(peak_dist ** 2))

    cliff_progress = (df["TyreLife"] - cliff_lap).clip(lower=0)
    df["TyreCliff"] = np.expm1(cliff_progress * TYRE_DEGRADE_FACTOR * 0.9 * compound_factor)

    df["TyreDegLinear"] = df["TyreLife"] * TYRE_DEGRADE_FACTOR * compound_factor
    df["TyreDegQuad"] = (df["TyreLife"] ** 2) * (TYRE_DEGRADE_FACTOR * 0.12) * compound_factor
    df["TyreDegExp"] = np.expm1(df["TyreLife"] * TYRE_DEGRADE_FACTOR * 0.65 * compound_factor)

    # Net tyre effect: warm-up/peak reduce lap time delta early, degradation increases it later
    df["Tyre_Degrade"] = (
        1
        + df["TyreDegLinear"]
        + df["TyreDegQuad"]
        + df["TyreDegExp"]
        + df["TyreCliff"]
        - (0.04 * df["TyreWarmup"])
        - (0.06 * df["TyrePeakGrip"])
    )

    df["TyreFuel"] = df["Tyre_Degrade"] * df["FuelEffect"]
    df["TyreFuelSq"] = (df["Tyre_Degrade"] ** 2) * df["FuelEffect"]
    df["TyreFuelSq"] = df["TyreFuel"] ** 2
    df["TyreFuelInteraction"] = (df["TyreDegLinear"] + df["TyreDegExp"] + df["TyreCliff"]) * df["FuelBurn"]
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
    group_cols = ["Driver", "Event", "Compound"]
    for col in ["LapDelta", "Sector1Time", "Sector2Time", "Sector3Time"]:
        shifted = df.groupby(["Driver", "Event", "Compound"])[col].shift(1)
        df[f"{col}_RollMean"] = shifted.rolling(ROLLING_WINDOW).mean().fillna(0)
        df[f"{col}_RollStd"] = shifted.rolling(ROLLING_WINDOW).std().fillna(0)
        shifted = df.groupby(group_cols)[col].shift(1)
        grouped_shifted = shifted.groupby([df[c] for c in group_cols])
        df[f"{col}_RollMean"] = (
            grouped_shifted.rolling(ROLLING_WINDOW, min_periods=1)
            .mean()
            .reset_index(level=[0, 1, 2], drop=True)
            .fillna(0)
        )
        df[f"{col}_RollStd"] = (
            grouped_shifted.rolling(ROLLING_WINDOW, min_periods=2)
            .std()
            .reset_index(level=[0, 1, 2], drop=True)
            .fillna(0)
        )
    return df


def _add_sector_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Each sector's share of the total lap time."""
    df["S1_Ratio"] = df["Sector1Time"] / df["LapTime"]
    df["S2_Ratio"] = df["Sector2Time"] / df["LapTime"]
    df["S3_Ratio"] = df["Sector3Time"] / df["LapTime"]
    return df
