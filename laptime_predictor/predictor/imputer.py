"""
SimulatorImputer — built and stored inside the .pkl at fit() time.

Learns historical median values for all columns that can't be known
at simulation time (LapTime, Sector1/2/3Time, BestLap).=
"""

from __future__ import annotations

import warnings

import pandas as pd

# Columns we need to impute for simulation
_IMPUTE_COLS = ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]

# Fallback chain: list of groupby key tuples, most → least specific
_FALLBACK_CHAIN = [
    ("Driver", "Event", "Compound"),
    ("Driver", "Compound"),
    ("Team", "Event", "Compound"),
    ("Event", "Compound"),
    ("Compound",),
]


class SimulatorImputer:
    """
    Fits on the full training DataFrame and stores lookup tables
    for every column in _IMPUTE_COLS plus BestLap.

    All tables are plain dicts → serialise cleanly inside the .pkl.
    """

    def __init__(self) -> None:
        # { col: { level: { key_tuple: median_value } } }
        self._tables: dict[str, dict[tuple, dict]] = {}
        self._global: dict[str, float] = {}

    # Fitting
    def fit(self, df: pd.DataFrame) -> "SimulatorImputer":
        """
        Learn medians from the cleaned, feature-engineered training DataFrame.
        Call this once inside F1LapPredictor.fit() before saving.
        """
        cols = _IMPUTE_COLS + ["BestLap"]

        for col in cols:
            self._tables[col] = {}
            for keys in _FALLBACK_CHAIN:
                self._tables[col][keys] = (
                    df.groupby(list(keys))[col]
                    .median()
                    .to_dict()
                )
            self._global[col] = float(df[col].median())

        return self

    # Imputation
    def impute(
            self,
            Driver: str,
            Team: str,
            Event: str,
            Compound: str,
            TyreLife: int | float,
            n_laps: int = 1,
    ) -> pd.DataFrame:
        """Build a synthetic DataFrame row (or rows) ready for build_features()."""
        lookup_key = {
            ("Driver", "Event", "Compound"): (Driver, Event, Compound),
            ("Driver", "Compound"): (Driver, Compound),
            ("Team", "Event", "Compound"): (Team, Event, Compound),
            ("Event", "Compound"): (Event, Compound),
            ("Compound",): (Compound,),
        }

        imputed = {}
        for col in _IMPUTE_COLS + ["BestLap"]:
            value = None
            for keys in _FALLBACK_CHAIN:
                key = lookup_key[keys]
                value = self._tables[col][keys].get(key)
                if value is not None:
                    break
            if value is None:
                warnings.warn(
                    f"No historical data found for {col} with the given inputs. "
                    f"Using global median ({self._global[col]:.3f}s).",
                    UserWarning,
                    stacklevel=3,
                )
                value = self._global[col]
            imputed[col] = value

        rows = []
        for i in range(n_laps):
            rows.append({
                "Driver": Driver,
                "Team": Team,
                "Event": Event,
                "Compound": Compound,
                "TyreLife": int(TyreLife) + i,
                "LapTime": imputed["LapTime"],
                "Sector1Time": imputed["Sector1Time"],
                "Sector2Time": imputed["Sector2Time"],
                "Sector3Time": imputed["Sector3Time"],
                "BestLap": imputed["BestLap"],
            })

        return pd.DataFrame(rows)

    # Introspection
    def known_drivers(self) -> list[str]:
        """List all drivers seen during training."""
        return sorted({k[0] for k in self._tables["LapTime"][("Driver", "Compound")]})

    def known_events(self) -> list[str]:
        """List all events seen during training."""
        return sorted({k[1] for k in self._tables["LapTime"][("Driver", "Event", "Compound")]})

    def known_compounds(self) -> list[str]:
        """List all compounds seen during training."""
        return sorted({k[0] for k in self._tables["LapTime"][("Compound",)]})

    def coverage(self, Driver: str, Event: str, Compound: str) -> str:
        """
        Report which fallback level will be used for a given combination.
        Useful for understanding confidence of a simulation.
        """
        lookup_key = {
            ("Driver", "Event", "Compound"): (Driver, Event, Compound),
            ("Driver", "Compound"): (Driver, Compound),
            ("Team", "Event", "Compound"): (Driver, Event, Compound),  # Team unknown here
            ("Event", "Compound"): (Event, Compound),
            ("Compound",): (Compound,),
        }
        for keys in _FALLBACK_CHAIN:
            key = lookup_key[keys]
            if self._tables["LapTime"][keys].get(key) is not None:
                return f"Matched at level: {' + '.join(keys)}"
        return "Global median fallback"
