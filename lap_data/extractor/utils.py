import os

import pandas as pd
import pycountry
from fuzzywuzzy import process


def clean_track_name(track_name: str) -> str:
    return track_name.replace(' Grand Prix', '').strip()


def generate_output_path(year=None, race_index=None, track_name=None, output_dir="data"):
    """
    Generate CSV file path(s) for storing F1 lap data.

    - No year -> data/all.csv (global)
    - Year only -> data/<year>/all.csv (all races in that year)
    - Year + race_index -> data/<year>/<race_index>_<country>.csv
    """
    os.makedirs(output_dir, exist_ok=True)

    # Global all.csv
    if year is None:
        return os.path.join(output_dir, "all.csv")

    # Year folder
    year_folder = os.path.join(output_dir, str(year))
    os.makedirs(year_folder, exist_ok=True)

    # Only year provided -> year/all.csv
    if race_index is None:
        return os.path.join(year_folder, "all.csv")

    # Year + race_index (optional country)
    race_file = f"{race_index}.csv"
    if track_name:
        country = gp_to_country(track_name)
        # Clean country name (remove spaces)
        country_clean = country.replace(" ", "_")
        race_file = f"{race_index}_{country_clean}.csv"

    return os.path.join(year_folder, race_file)


def ensure_cache_folder(folder: str):
    os.makedirs(folder, exist_ok=True)
    return folder


def append_to_csv(df: pd.DataFrame, filepath: str, unique_cols=None):
    """
    Append df to CSV at filepath, avoiding duplicates.

    - unique_cols: list of columns to identify duplicates.
      If None, will use all columns.
    """
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        combined = pd.concat([existing_df, df], ignore_index=True)
    else:
        combined = df.copy()

    # Drop duplicates
    if unique_cols:
        combined.drop_duplicates(subset=unique_cols, inplace=True)
    else:
        combined.drop_duplicates(inplace=True)

    # Save
    combined.to_csv(filepath, index=False)


def gp_to_country(track_name):
    # Remove 'Grand Prix'
    name = track_name.replace("Grand Prix", "").strip()

    # Try exact match with pycountry
    country = pycountry.countries.get(name=name)
    if country:
        return country.name

    # If exact match fails, use fuzzy matching
    all_country_names = [c.name for c in pycountry.countries]
    match, score = process.extractOne(name, all_country_names)
    if score > 80:
        return match

    # fallback
    return name
