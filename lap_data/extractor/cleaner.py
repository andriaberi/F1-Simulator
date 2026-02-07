from lap_data.extractor.utils import gp_to_country
from lap_data.config.settings import DEFAULT_COLUMNS


def infer_weather_from_tyre(compound):
    compound = str(compound).upper()
    if compound in ['INTERMEDIATE', 'WET']:
        return 'wet'
    return 'dry'


def clean_lap_data(df, track_name):
    """Keep only essential columns, add Racetrack, Weather, and TyreLap"""
    cols = DEFAULT_COLUMNS
    df_clean = df[[c for c in cols if c in df.columns]].copy()

    # Racetrack
    df_clean['Racetrack'] = gp_to_country(track_name)

    # Weather
    df_clean['Weather'] = df_clean['Compound'].apply(infer_weather_from_tyre)

    return df_clean
