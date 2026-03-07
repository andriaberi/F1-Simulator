from __future__ import annotations

from itertools import product as iterproduct
from typing import Optional

from pandas import Series

from laptime_predictor import F1LapPredictor
from simulator.config import EVENTS
from simulator.strategy.constraints import _is_valid_compound_combo
from simulator.strategy.models import StintConfig, StrategyResult


def _get_n_laps(event: str) -> int:
    return next(item["lap_number"] for item in EVENTS if item["event"] == event)


def _precompute_laptimes(
        predictor: F1LapPredictor,
        compounds: list[str],
        driver_id: str,
        team: str,
        event: str,
        n_laps: int,
) -> dict[str, Series]:
    return {
        compound: predictor.simulate(
            Driver=driver_id,
            Team=team,
            Event=event,
            Compound=compound,
            TyreLife=1,
            n_laps=n_laps,
            verbose=False,
        )
        for compound in compounds
    }


def _compute_stint_time(laptimes: Series, stint_len: int) -> float:
    max_age = int(laptimes.index.max())
    return sum(laptimes.loc[min(lap, max_age)] for lap in range(1, stint_len + 1))


def _search_one_stop(
    compounds: list[str],
    laptimes: dict[str, Series],
    config: StintConfig,
    must_use_multiple: bool,
    weather: str,
    pit_time: float,
) -> Optional[StrategyResult]:
    best_time = float("inf")
    best_result: Optional[StrategyResult] = None

    stop1_min = int(config.n_laps * 0.35)
    stop1_max = int(config.n_laps * 0.65)
    max_stint = int(config.n_laps * 0.70)

    for stop1 in range(stop1_min, stop1_max + 1):
        stint_lengths = [stop1, config.n_laps - stop1]

        if any(l < config.min_stint or l > max_stint for l in stint_lengths):
            continue

        for combo in iterproduct(compounds, repeat=2):
            if must_use_multiple and len(set(combo)) < 2:
                continue
            if weather == "Dry" and combo[0] == "HARD":
                continue
            if combo[0] == combo[1]:
                continue

            total_time = (
                _compute_stint_time(laptimes[combo[0]], stint_lengths[0]) + pit_time
                + _compute_stint_time(laptimes[combo[1]], stint_lengths[1])
            )

            if total_time < best_time:
                best_time = total_time
                best_result = StrategyResult(
                    stints=combo,
                    stop_laps=[stop1],
                    stint_lengths=stint_lengths,
                    total_time=total_time,
                )

    return best_result


def _search_two_stop(
    compounds: list[str],
    laptimes: dict[str, Series],
    config: StintConfig,
    must_use_multiple: bool,
    weather: str,
    pit_time: float,
) -> Optional[StrategyResult]:
    best_time = float("inf")
    best_result: Optional[StrategyResult] = None

    for stop1 in range(config.stop1_min, config.stop1_max + 1):
        stop2_start = stop1 + config.min_stint
        stop2_end = config.n_laps - config.min_stint

        for stop2 in range(stop2_start, stop2_end + 1):
            stint_lengths = [stop1, stop2 - stop1, config.n_laps - stop2]

            if any(l < config.min_stint or l > config.max_stint for l in stint_lengths):
                continue

            for combo in iterproduct(compounds, repeat=3):
                if not _is_valid_compound_combo(combo, must_use_multiple, weather):
                    continue

                total_time = sum(
                    _compute_stint_time(laptimes[comp], length) + (pit_time if i < 2 else 0)
                    for i, (comp, length) in enumerate(zip(combo, stint_lengths))
                )

                if total_time < best_time:
                    best_time = total_time
                    best_result = StrategyResult(
                        stints=combo,
                        stop_laps=[stop1, stop2],
                        stint_lengths=stint_lengths,
                        total_time=total_time,
                    )

    return best_result


_STRATEGY_SEARCH = {
    "One Stop": _search_one_stop,
    "Two Stop": _search_two_stop,
}


def _search_best_strategy(
    strategy_type: str,
    compounds: list[str],
    laptimes: dict[str, Series],
    config: StintConfig,
    must_use_multiple: bool,
    weather: str,
    pit_time: float,
) -> Optional[StrategyResult]:
    search_fn = _STRATEGY_SEARCH.get(strategy_type)
    if search_fn is None:
        raise ValueError(f"Unknown strategy type '{strategy_type}'. Choose from: {list(_STRATEGY_SEARCH)}")

    return search_fn(compounds, laptimes, config, must_use_multiple, weather, pit_time)
