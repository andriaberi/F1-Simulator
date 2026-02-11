"""
Programmatic entry point for the laptime_predictor package.
Import and use this when integrating into another project.
"""

from __future__ import annotations

import pandas as pd

from laptime_predictor.predictor import F1LapPredictor
from laptime_predictor.config import DEFAULT_MODEL_PATH, DEFAULT_DATA_PATH


def train(
    data_path: str = DEFAULT_DATA_PATH,
    save_path: str = DEFAULT_MODEL_PATH,
    lgbm_params: dict | None = None,
    verbose: int = 200,
) -> F1LapPredictor:
    """Train a new model and save it to disk."""
    predictor = F1LapPredictor(lgbm_params=lgbm_params, verbose_eval=verbose)
    predictor.fit(data_path)
    predictor.save(save_path)
    return predictor


def predict(
    data_path: str = DEFAULT_DATA_PATH,
    model_path: str = DEFAULT_MODEL_PATH,
) -> pd.Series:
    """Load a saved model and return predicted lap times for *data_path*."""
    predictor = F1LapPredictor.load(model_path)
    return predictor.predict(data_path)


def evaluate(
    data_path: str = DEFAULT_DATA_PATH,
    model_path: str = DEFAULT_MODEL_PATH,
) -> float:
    """Load a saved model and print/return MAE on *data_path*."""
    predictor = F1LapPredictor.load(model_path)
    return predictor.evaluate(data_path)


def load(model_path: str = DEFAULT_MODEL_PATH) -> F1LapPredictor:
    """Convenience wrapper to load a saved predictor."""
    return F1LapPredictor.load(model_path)
