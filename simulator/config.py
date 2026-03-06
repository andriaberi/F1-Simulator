ALL_DRIVERS = [
    {"name": "Lando Norris",        "team": "McLaren",         "id": "NOR"},
    {"name": "Oscar Piastri",       "team": "McLaren",         "id": "PIA"},
    {"name": "Max Verstappen",      "team": "Red Bull Racing", "id": "VER"},
    {"name": "Yuki Tsunoda",        "team": "Red Bull Racing", "id": "TSU"},
    {"name": "Charles Leclerc",     "team": "Ferrari",         "id": "LEC"},
    {"name": "Lewis Hamilton",      "team": "Ferrari",         "id": "HAM"},
    {"name": "George Russell",      "team": "Mercedes",        "id": "RUS"},
    {"name": "Andrea Kimi Antonelli","team": "Mercedes",       "id": "ANT"},
    {"name": "Fernando Alonso",     "team": "Aston Martin",    "id": "ALO"},
    {"name": "Lance Stroll",        "team": "Aston Martin",    "id": "STR"},
    {"name": "Pierre Gasly",        "team": "Alpine",          "id": "GAS"},
    {"name": "Franco Colopinto",    "team": "Alpine",          "id": "COL"},
    {"name": "Esteban Ocon",        "team": "Haas F1 Team",    "id": "OCO"},
    {"name": "Oliver Bearman",      "team": "Haas F1 Team",    "id": "BEA"},
    {"name": "Isack Hadjar",        "team": "Racing Bulls",    "id": "HAD"},
    {"name": "Liam Lawson",         "team": "Racing Bulls",    "id": "LAW"},
    {"name": "Alex Albon",          "team": "Williams",        "id": "ALB"},
    {"name": "Carlos Sainz",        "team": "Williams",        "id": "SAI"},
    {"name": "Nico Hülkenberg",     "team": "Kick Sauber",     "id": "HUL"},
    {"name": "Gabriel Bortoleto",   "team": "Kick Sauber",     "id": "BOR"},
]

DRIVERS = [item["name"] for item in ALL_DRIVERS]
TEAMS = [item["team"] for item in ALL_DRIVERS]
IDS = [item["id"] for item in ALL_DRIVERS]

EVENTS = [
    {"event": "Australian Grand Prix", "lap_number": 58},
    {"event": "Chinese Grand Prix", "lap_number": 56},
    {"event": "Japanese Grand Prix", "lap_number": 53},
    {"event": "Bahrain Grand Prix", "lap_number": 57},
    {"event": "Saudi Arabian Grand Prix", "lap_number": 50},
    {"event": "Miami Grand Prix", "lap_number": 57},
    {"event": "Emilia Romagna Grand Prix", "lap_number": 63},
    {"event": "Monaco Grand Prix", "lap_number": 78},
    {"event": "Spanish Grand Prix", "lap_number": 66},
    {"event": "Canadian Grand Prix", "lap_number": 70},
    {"event": "Austrian Grand Prix", "lap_number": 71},
    {"event": "British Grand Prix", "lap_number": 52},
    {"event": "Belgian Grand Prix", "lap_number": 44},
    {"event": "Hungarian Grand Prix", "lap_number": 70},
    {"event": "Dutch Grand Prix", "lap_number": 72},
    {"event": "Italian Grand Prix", "lap_number": 53},
    {"event": "Azerbaijan Grand Prix", "lap_number": 51},
    {"event": "Singapore Grand Prix", "lap_number": 62},
    {"event": "United States Grand Prix", "lap_number": 56},
    {"event": "Mexico City Grand Prix", "lap_number": 71},
    {"event": "São Paulo Grand Prix", "lap_number": 71},
    {"event": "Las Vegas Grand Prix", "lap_number": 50},
    {"event": "Qatar Grand Prix", "lap_number": 57},
    {"event": "Abu Dhabi Grand Prix", "lap_number": 58},
]

DEFAULT_MODEL_PATH = "train/model.pkl"