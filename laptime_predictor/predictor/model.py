"""F1LapPredictor: the main class for training, evaluating, saving, and loading."""
from __future__ import annotations

import pickle
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupShuffleSplit

from laptime_predictor.config import (
    FEATURES,
    LGBM_PARAMS,
    DEFAULT_TEST_SIZE,
    DEFAULT_RANDOM_STATE,
    DEFAULT_EARLY_STOPPING,
    DEFAULT_VERBOSE_EVAL,
    DEFAULT_MODEL_PATH,
)
from laptime_predictor.predictor.features import build_features, encode_categoricals
from laptime_predictor.predictor.imputer import SimulatorImputer
from laptime_predictor.predictor.utils import load_data, clean_data, delta_to_laptime


class F1LapPredictor:
    """Train, evaluate, save, and load an F1 lap-time prediction model."""

    def __init__(
            self,
            lgbm_params: dict | None = None,
            test_size: float = DEFAULT_TEST_SIZE,
            early_stopping_rounds: int = DEFAULT_EARLY_STOPPING,
            verbose_eval: int = DEFAULT_VERBOSE_EVAL,
    ) -> None:
        params = {**LGBM_PARAMS}
        if lgbm_params:
            params.update(lgbm_params)

        self.model = lgb.LGBMRegressor(**params)
        self.test_size = test_size
        self.early_stopping_rounds = early_stopping_rounds
        self.verbose_eval = verbose_eval

        self._is_fitted: bool = False
        self.train_mae_: float | None = None
        self.test_mae_: float | None = None
        self.feature_importance_: pd.Series | None = None
        self.imputer_: SimulatorImputer | None = None

    # Training
    def fit(
            self,
            source: str | pd.DataFrame,
            random_state: int = DEFAULT_RANDOM_STATE,
    ) -> "F1LapPredictor":
        """Load, clean, engineer features, and train the model."""
        df = clean_data(load_data(source))
        df = build_features(df)

        X = encode_categoricals(df[FEATURES])
        y = df["LapDelta"]

        gss = GroupShuffleSplit(n_splits=1, test_size=self.test_size, random_state=random_state)
        train_idx, test_idx = next(gss.split(X, y, groups=df["Event"]))

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        callbacks = [
            lgb.early_stopping(stopping_rounds=self.early_stopping_rounds, verbose=False),
            lgb.log_evaluation(self.verbose_eval),
        ]

        self.model.fit(
            X_train, y_train,
            categorical_feature=["Team", "Compound"],
            eval_set=[(X_test, y_test)],
            eval_metric="mae",
            callbacks=callbacks,
        )

        # Record metrics
        self.train_mae_ = mean_absolute_error(
            df.iloc[train_idx]["LapTime"],
            delta_to_laptime(self.model.predict(X_train), df.iloc[train_idx]["BestLap"].values),
        )
        self.test_mae_ = mean_absolute_error(
            df.iloc[test_idx]["LapTime"],
            delta_to_laptime(self.model.predict(X_test), df.iloc[test_idx]["BestLap"].values),
        )
        self.feature_importance_ = pd.Series(
            self.model.feature_importances_, index=FEATURES
        ).sort_values(ascending=False)
        self.imputer_ = SimulatorImputer().fit(df)
        self._is_fitted = True

        print(f"\n{'=' * 40}")
        print(f"  Train MAE : {self.train_mae_:.3f} s")
        print(f"  Test  MAE : {self.test_mae_:.3f} s")
        print(f"{'=' * 40}\n")
        return self

    # Inference
    def predict(self, source: str | pd.DataFrame) -> pd.Series:
        """Predict lap times (seconds) for every row in *source*."""
        self._check_fitted()
        df = clean_data(load_data(source))
        df = build_features(df)
        X = encode_categoricals(df[FEATURES])
        preds = delta_to_laptime(self.model.predict(X), df["BestLap"].values)
        return pd.Series(preds, index=df.index, name="PredictedLapTime")

    def evaluate(self, source: str | pd.DataFrame) -> float:
        """Compute and print MAE against the true LapTime column."""
        self._check_fitted()
        df = clean_data(load_data(source))
        df = build_features(df)
        X = encode_categoricals(df[FEATURES])
        preds = delta_to_laptime(self.model.predict(X), df["BestLap"].values)
        mae = mean_absolute_error(df["LapTime"], preds)
        print(f"MAE: {mae:.3f} s")
        return mae

    def feature_importance(self, top_n: int = 20) -> pd.Series:
        """Return the top-N most important features."""
        self._check_fitted()
        return self.feature_importance_.head(top_n)

    # Simulation
    def simulate(
            self,
            Driver: str,
            Team: str,
            Event: str,
            Compound: str,
            TyreLife: int | float,
            n_laps: int = 1,
            verbose: bool = True,
    ) -> pd.Series:
        """
        Predict lap time(s) from only the 5 inputs you have.
        All missing columns are imputed from historical training data
        stored inside this model — no CSV needed.
        """
        self._check_fitted()

        if verbose:
            level = self.imputer_.coverage(Driver, Event, Compound)
            print(f"Imputation — {level}")

        # Build synthetic rows with imputed static columns
        df_sim = self.imputer_.impute(
            Driver=Driver,
            Team=Team,
            Event=Event,
            Compound=Compound,
            TyreLife=TyreLife,
            n_laps=n_laps,
        )

        # Engineer features and predict
        df_sim = build_features(df_sim)
        X = encode_categoricals(df_sim[FEATURES])
        preds = delta_to_laptime(self.model.predict(X), df_sim["BestLap"].values)

        index = range(int(TyreLife), int(TyreLife) + n_laps)
        return pd.Series(preds, index=index, name="PredictedLapTime")

    def known_drivers(self) -> list[str]:
        """List all drivers seen during training."""
        self._check_fitted()
        return self.imputer_.known_drivers()

    def known_events(self) -> list[str]:
        """List all events seen during training."""
        self._check_fitted()
        return self.imputer_.known_events()

    def known_compounds(self) -> list[str]:
        """List all compounds seen during training."""
        self._check_fitted()
        return self.imputer_.known_compounds()

    # Persistence
    def save(self, path: str | Path = DEFAULT_MODEL_PATH) -> None:
        """Serialise the fitted predictor to *path* using pickle."""
        self._check_fitted()
        path = Path(path)
        with path.open("wb") as fh:
            pickle.dump(self, fh)
        print(f"Model saved → {path.resolve()}")

    @classmethod
    def load(cls, path: str | Path = DEFAULT_MODEL_PATH) -> "F1LapPredictor":
        """Load a previously saved predictor from *path*."""
        path = Path(path)
        with path.open("rb") as fh:
            obj = pickle.load(fh)
        if not isinstance(obj, cls):
            raise TypeError(f"Expected F1LapPredictor, got {type(obj)}")
        print(f"Model loaded ← {path.resolve()}  (test MAE: {obj.test_mae_:.3f} s)")
        return obj

    # Internals
    def _check_fitted(self) -> None:
        if not self._is_fitted:
            raise RuntimeError("Model is not fitted yet. Call .fit() first.")

    def __repr__(self) -> str:
        status = f"test_mae={self.test_mae_:.3f}s" if self._is_fitted else "not fitted"
        return f"F1LapPredictor({status})"
