import logging
import sys
import warnings

import pandas as pd

from .config.settings import YEARS, DEFAULT_COLUMNS
from .extractor.cleaner import clean_lap_data
from .extractor.fastf1_fetcher import fetch_laps
from .extractor.utils import generate_output_path, append_to_csv

# Silence fuzzywuzzy warning and reduce FastF1/request logs
warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher.*")
logging.getLogger('fastf1').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

UNIQUE_LAP_COLS = list(set(DEFAULT_COLUMNS))  # Columns used to deduplicate laps


def run_pipeline(year: int = None, race_index: int = None):
    """
    Extract F1 lap data for a specific year and optional race_index.
    Saves CSV only for the specific race (or all races of the year if race_index is None).
    """

    # Validate year input
    if year is None:
        print("Error: Year must be provided for specific CSV output.")
        sys.exit(1)
    if year not in YEARS:
        print(f"Error: Year {year} is invalid. Must be between {YEARS[0]} and {YEARS[-1]}.")
        sys.exit(1)

    # Fetch schedule for the year
    try:
        from fastf1 import get_event_schedule
        schedule = get_event_schedule(year)
    except Exception:
        print(f"Error: Failed to fetch schedule for year {year}. Exiting.")
        sys.exit(1)

    # Filter only Grand Prix races
    tracks = [t for t in schedule['EventName'].tolist() if 'Grand Prix' in t]

    # Validate race_index input
    if race_index is not None:
        if not (1 <= race_index <= len(tracks)):
            print(f"Error: Race index {race_index} is invalid for year {year}. Must be between 1 and {len(tracks)}.")
            sys.exit(1)
        tracks = [tracks[race_index - 1]]  # Only process selected race

    print(f"\nProcessing year: {year}")
    all_laps = []

    # Process each racetrack
    for idx, track in enumerate(tracks, start=1):
        prefix = f"  Race {idx}: {track} - "
        try:
            laps_df = fetch_laps(year, track)          # Fetch lap data from FastF1
            df_clean = clean_lap_data(laps_df, track) # Clean and structure lap data
            all_laps.append((df_clean, track))
            print(f"{prefix}Success")
        except Exception as e:
            print(f"{prefix}Failed ({e})")
            continue

    # Save cleaned data to CSV per race
    for df, track_name in all_laps:
        output_file = generate_output_path(year=year, race_index=race_index, track_name=track_name)
        append_to_csv(df, output_file, unique_cols=UNIQUE_LAP_COLS)

    # Summary of extraction
    print(f"\nSaved {len(all_laps)} race(s) for year {year}")
