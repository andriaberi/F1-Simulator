"""
All constants, feature lists, and default hyperparameters.
Edit here to change model behaviour globally.
"""

# Data
REQUIRED_COLS = [
    "Driver", "Team", "Compound", "TyreLife",
    "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "Event",
]

CATEGORICAL_FEATURES = ["Team", "Compound"]

FEATURES = [
    "Team", "Compound",
    "TyreLife", "Tyre_Degrade", "FuelProxy", "FuelEffect",
    "TyreFuel", "TyreFuelSq",
    "LapNorm", "LapDeltaPrev",
    "Sector1Time_Norm", "Sector2Time_Norm", "Sector3Time_Norm",
    "StintLap", "TyreLifeSq", "TyreLifeLog",
    "TyreWarmup", "TyrePeakGrip", "TyreCliff",
    "TyreDegLinear", "TyreDegQuad", "TyreDegExp",
    "FuelLoadStart", "FuelBurn", "FuelRemaining",
    "TyreFuelInteraction",
    "Sector1Time_PrevDelta", "Sector2Time_PrevDelta", "Sector3Time_PrevDelta",
    "S1_Ratio", "S2_Ratio", "S3_Ratio",
    "LapDelta_RollMean", "LapDelta_RollStd",
    "Sector1Time_RollMean", "Sector1Time_RollStd",
    "Sector2Time_RollMean", "Sector2Time_RollStd",
    "Sector3Time_RollMean", "Sector3Time_RollStd",
]

# Feature engineering
ROLLING_WINDOW: int = 3
FUEL_LOAD_FACTOR: float = 0.0015  # per-lap fuel weight penalty
TYRE_DEGRADE_FACTOR: float = 0.003  # per-lap tyre degradation
OUTLIER_QUANTILE: float = 0.995  # remove top 0.5% lap times

COMPOUND_DEGRADE_MULTIPLIER: dict[str, float] = {
    "SOFT": 1.25,
    "MEDIUM": 1.00,
    "HARD": 0.80,
    "INTERMEDIATE": 1.10,
    "WET": 1.15,
}


COMPOUND_WARMUP_LAPS: dict[str, float] = {
    "SOFT": 2.0,
    "MEDIUM": 3.0,
    "HARD": 4.0,
    "INTERMEDIATE": 3.0,
    "WET": 3.0,
}

COMPOUND_PEAK_LAP: dict[str, float] = {
    "SOFT": 4.0,
    "MEDIUM": 7.0,
    "HARD": 10.0,
    "INTERMEDIATE": 6.0,
    "WET": 6.0,
}

COMPOUND_CLIFF_LAP: dict[str, float] = {
    "SOFT": 14.0,
    "MEDIUM": 22.0,
    "HARD": 30.0,
    "INTERMEDIATE": 18.0,
    "WET": 16.0,
}

# Training
DEFAULT_TEST_SIZE: float = 0.2
DEFAULT_RANDOM_STATE: int = 42
DEFAULT_EARLY_STOPPING: int = 200
DEFAULT_VERBOSE_EVAL: int = 200

LGBM_PARAMS: dict = dict(
    n_estimators=6000,
    learning_rate=0.01,
    num_leaves=128,
    max_depth=10,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="mae",
    random_state=DEFAULT_RANDOM_STATE,
    force_col_wise=True,
)

# Persistence
DEFAULT_MODEL_PATH: str = "train/model.pkl"
DEFAULT_DATA_PATH: str = "data/all.csv"