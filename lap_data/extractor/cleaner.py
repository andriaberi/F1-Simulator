from lap_data.config.settings import DEFAULT_COLUMNS

def clean_lap_data(df, track_name):
    """Keep only essential columns, and add Race Event column"""
    cols = DEFAULT_COLUMNS
    df_clean = df[[c for c in cols if c in df.columns]].copy()

    # Event
    df_clean['Event'] = track_name

    return df_clean