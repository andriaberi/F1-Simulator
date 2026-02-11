"""
Enables:  python -m laptime_predictor <command> [options]
"""

import sys
from laptime_predictor.cli import run

run(sys.argv[1:])
