import fastf1


def fetch_laps(year, track):
    """Fetch laps from FastF1 for a given year and track"""
    session = fastf1.get_session(year, track, 'R')  # Race session
    session.load()
    laps = session.laps

    # Convert LapTime to seconds
    laps['LapTime'] = laps['LapTime'].dt.total_seconds()
    return laps
