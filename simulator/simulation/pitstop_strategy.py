from InquirerPy import inquirer

from simulator.config import *

from laptime_predictor.predictor import F1LapPredictor


def simulate_pitstop_strategy(driver_id: str, team: str, event: str, weather: str, pit_time=25):
    from itertools import product as iterproduct
    predictor = F1LapPredictor.load(DEFAULT_MODEL_PATH)

    print("Simulating Pitstop Strategy...")

    if weather == "Dry":
        compounds = ["SOFT", "MEDIUM", "HARD"]
        must_use_multiple = True
    else:
        compounds = ["INTERMEDIATE", "WET"]
        must_use_multiple = False

    n_laps = next(item["lap_number"] for item in EVENTS if item["event"] == event)

    # --- Balanced stint constraints ---
    min_stint = max(10, n_laps // 10)  # ~10% of race minimum
    max_stint = n_laps * 45 // 100  # ~45% of race maximum per stint

    # Stop windows: divide race into roughly equal thirds
    stop1_min = n_laps * 20 // 100  # Earliest lap 20%
    stop1_max = n_laps * 40 // 100  # Latest lap 40%
    stop2_min_offset = min_stint  # At least min_stint after stop1
    stop2_max_before_end = min_stint  # At least min_stint before finish

    # Precompute laptimes per compound
    results = {}
    for compound in compounds:
        results[compound] = predictor.simulate(
            Driver=driver_id,
            Team=team,
            Event=event,
            Compound=compound,
            TyreLife=1,
            n_laps=n_laps,
            verbose=False,
        )

    # Print lap table
    col_width = 12
    header = ["Lap"] + compounds
    print("\n" + "".join(h.center(col_width) for h in header))
    print("-" * col_width * len(header))
    for lap in range(1, n_laps + 1):
        row = [str(lap)]
        for compound in compounds:
            laptime = results[compound].get(lap, results[compound][max(results[compound].keys())])
            row.append(f"{laptime:.3f}" if isinstance(laptime, float) else laptime)
        print("".join(cell.center(col_width) for cell in row))
    print()

    best_total = float("inf")
    best_plan = None

    for stop1 in range(stop1_min, stop1_max + 1):
        stop2_start = stop1 + stop2_min_offset
        stop2_end = n_laps - stop2_max_before_end

        for stop2 in range(stop2_start, stop2_end + 1):
            stint1_len = stop1
            stint2_len = stop2 - stop1
            stint3_len = n_laps - stop2

            # ✅ Enforce max stint length on ALL three stints
            if stint1_len > max_stint:
                continue
            if stint2_len > max_stint:
                continue
            if stint3_len > max_stint:
                continue

            # ✅ Enforce min stint on all stints
            if stint1_len < min_stint or stint2_len < min_stint or stint3_len < min_stint:
                continue

            for stint_compounds in iterproduct(compounds, repeat=3):
                if must_use_multiple and len(set(stint_compounds)) < 2:
                    continue
                if weather == "Dry" and stint_compounds[0] == "HARD":
                    continue
                if stint_compounds[0] == stint_compounds[1] or stint_compounds[1] == stint_compounds[2]:
                    continue

                total_time = 0
                stints = [
                    (stint_compounds[0], stint1_len),
                    (stint_compounds[1], stint2_len),
                    (stint_compounds[2], stint3_len),
                ]

                for idx, (comp, stint_len) in enumerate(stints):
                    for lap_age in range(1, stint_len + 1):
                        lap_index = min(lap_age, max(results[comp].keys()))
                        total_time += results[comp][lap_index]
                    if idx < 2:
                        total_time += pit_time

                if total_time < best_total:
                    best_total = total_time
                    best_plan = {
                        "stints": stint_compounds,
                        "stops": [stop1, stop2],
                        "total_time": best_total,
                        "stint_lengths": [stint1_len, stint2_len, stint3_len],
                    }

    print("=" * 50)
    print("Best 2-Stop Strategy (Realistic):")
    if best_plan:
        print(f" Stints:        {best_plan['stints']}")
        print(f" Pit stops at:  Lap {best_plan['stops'][0]} → Lap {best_plan['stops'][1]}")
        print(f" Stint lengths: {best_plan['stint_lengths']} laps")
        print(f" Total time:    {best_plan['total_time']:.3f}s")
    else:
        print("No valid strategy found. Try relaxing stint constraints.")
    print("=" * 50)