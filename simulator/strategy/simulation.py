from __future__ import annotations

from typing import Optional

from simulator.config import EVENTS, DEFAULT_MODEL_PATH
from laptime_predictor.predictor import F1LapPredictor
from simulator.strategy.constraints import _get_compounds
from simulator.strategy.models import StintConfig
from simulator.strategy.search import _get_n_laps, _precompute_laptimes, _search_best_strategy


def simulate_pitstop_strategy(
    driver_id: str,
    team: str,
    event: str,
    weather: str,
    strategy: str,
    pit_time: float = 25.0,
) -> None:
    predictor = F1LapPredictor.load(DEFAULT_MODEL_PATH)
    compounds, must_use_multiple = _get_compounds(weather)
    n_laps = _get_n_laps(event)
    config = StintConfig(n_laps=n_laps)

    print("Simulating pit stop strategy...")

    laptimes = _precompute_laptimes(predictor, compounds, driver_id, team, event, n_laps)
    result = _search_best_strategy(
        strategy, compounds, laptimes, config, must_use_multiple, weather, pit_time
    )

    if result:
        result.display()
    else:
        print("No valid strategy found. Try relaxing stint constraints.")