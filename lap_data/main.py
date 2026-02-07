import logging
import os
import shutil
import sys
import warnings

import fastf1
import pandas as pd

from .config.settings import YEARS, DEFAULT_COLUMNS
from .extractor.cleaner import clean_lap_data
from .extractor.fastf1_fetcher import fetch_laps
from .extractor.utils import (
    generate_output_path,
    append_to_csv
)

# Filter fuzzywuzzy warning
warnings.filterwarnings(
    "ignore",
    message="Using slow pure-python SequenceMatcher.*"
)

# Silence FastF1 and requests logs
logging.getLogger('fastf1').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Columns to uniquely identify a lap for deduplication
UNIQUE_LAP_COLS = list(set(DEFAULT_COLUMNS))

def run_pipeline(year=None, race_index=None):
    """
    Extract F1 lap data for given year/race_index.
    Saves CSVs at three levels: global all, year all, per-race, with deduplication.
    """
    tracks = []
    all_laps = []

    # Validate year
    if year is not None and year not in YEARS:
        print(f"Error: Year {year} is invalid. Must be between {YEARS[0]} and {YEARS[-1]}.")
        sys.exit(1)

    # Determine years to process
    years_to_process = [year] if year else YEARS

    for y in years_to_process:
        print(f"\nProcessing year: {y}")

        # Get schedule
        try:
            from fastf1 import get_event_schedule
            schedule = get_event_schedule(y)
        except Exception:
            print(f"Error: Failed to fetch schedule for year {y}. Exiting.")
            sys.exit(1)

        # Filter only Grand Prix races
        tracks = [t for t in schedule['EventName'].tolist() if 'Grand Prix' in t]

        # Validate race_index
        if race_index is not None:
            if not (1 <= race_index <= len(tracks)):
                print(f"Error: Race index {race_index} is invalid for year {y}. Must be between 1 and {len(tracks)}.")
                sys.exit(1)
            tracks = [tracks[race_index - 1]]  # Only selected race

        # Process each track
        for idx, track in enumerate(tracks, start=1):
            print(f"  - Processing Track {idx}: {track}")
            try:
                laps_df = fetch_laps(y, track)
                df_clean = clean_lap_data(laps_df, track)
                all_laps.append((df_clean, track))
            except Exception as e:
                print(f"  Failed to process {track} {y}: {e}")
                continue

        # Write CSVs per year / race
        if all_laps:
            # Global all.csv
            combined_df = pd.concat([df for df, _ in all_laps], ignore_index=True)
            append_to_csv(combined_df, generate_output_path(), unique_cols=UNIQUE_LAP_COLS)

            # Year-level CSV
            year_dfs = [df for (df, track_name) in all_laps]
            if year_dfs:
                year_df = pd.concat(year_dfs, ignore_index=True)
                append_to_csv(year_df, generate_output_path(year=y), unique_cols=UNIQUE_LAP_COLS)

            # Per-race CSVs
            for df, track_name in all_laps:
                race_idx = race_index if race_index is not None else None
                output_file = generate_output_path(year=y, race_index=race_idx, track_name=track_name)
                append_to_csv(df, output_file, unique_cols=UNIQUE_LAP_COLS)

    # Summary of saved files
    print("\nSaved data to:")
    print(f"  - Global: {generate_output_path()}")
    for y in years_to_process:
        print(f"  - Year {y}: {generate_output_path(year=y)}")
    if race_index is not None and len(tracks) == 1:
        print(f"  - Race {race_index}: {generate_output_path(year=y, race_index=race_index, track_name=tracks[0])}")
