import fastf1


def fetch_laps(year, track):
    """Fetch laps from FastF1 for a given year and track"""
    session = fastf1.get_session(year, track, 'R')  # Race session
    session.load()
    laps = session.laps

    # Convert time to seconds
    for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
        laps[col] = laps[col].dt.total_seconds()

    return laps
