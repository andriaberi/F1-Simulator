import logging
import warnings
import time
from pathlib import Path

import fastf1

from .config.settings import YEARS, DEFAULT_COLUMNS
from .extractor.cleaner import clean_lap_data
from .extractor.fastf1_fetcher import fetch_laps
from .extractor.utils import generate_output_path, append_to_csv

# FastF1 + logging setup
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"

# Create cache directory if missing
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Enable FastF1 cache
fastf1.Cache.enable_cache(str(CACHE_DIR))

warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher.*")
logging.getLogger("fastf1").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

UNIQUE_LAP_COLS = list(set(DEFAULT_COLUMNS))


def run_pipeline(year: int = None, race_index: int = None):
    """
    Extract F1 lap data for a specific year and optional race_index.
    Saves ONE CSV per race.
    """

    years_to_process = [year] if year else YEARS

    for y in years_to_process:
        if y not in YEARS:
            print(f"[ERROR] Year {y} is invalid.")
            continue

        print(f"\nProcessing year: {y}")

        # Fetch schedule (cheap)
        try:
            schedule = fastf1.get_event_schedule(y)
        except Exception as e:
            print(f"[ERROR] Failed to fetch schedule for {y}: {e}")
            continue

        tracks = [
            name for name in schedule["EventName"].tolist()
            if "Grand Prix" in name
        ]

        if race_index is not None:
            if not (1 <= race_index <= len(tracks)):
                print(
                    f"[ERROR] Race index {race_index} invalid "
                    f"(1–{len(tracks)})"
                )
                continue
            tracks = [tracks[race_index - 1]]

        saved = 0

        # Process races
        for idx, track in enumerate(tracks, start=1):
            prefix = f"  Race {idx}: {track} - "

            try:
                laps_df = fetch_laps(y, track)              # should call session.load ONCE
                df_clean = clean_lap_data(laps_df, track)

                output_targets = [
                    {"year": None, "race_index": None},  # global
                    {"year": y, "race_index": None},  # per-year
                    {"year": y, "race_index": race_index if race_index is not None else idx},
                ]

                for target in output_targets:
                    output_file = generate_output_path(
                        year=target["year"],
                        race_index=target["race_index"],
                    )

                    append_to_csv(
                        df_clean,
                        output_file,
                        unique_cols=UNIQUE_LAP_COLS,
                    )

                saved += 1
                print(f"{prefix}Saved")

                time.sleep(1.5)  # REQUIRED throttle

            except Exception as e:
                print(f"{prefix}Failed ({e})")
                time.sleep(2)
                continue

        print(f"  Saved {saved} race(s) for year {y}")
