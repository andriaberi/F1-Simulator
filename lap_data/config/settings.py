from datetime import datetime

DEFAULT_CACHE_FOLDER = "cache"
CURRENT_YEAR = datetime.now().year
YEARS = list(range(2018, CURRENT_YEAR + 1))
DEFAULT_COLUMNS = ['Driver', 'Team', 'Compound', 'TyreLife', 'LapTime']
