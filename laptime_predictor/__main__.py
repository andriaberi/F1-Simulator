"""
Enables:  python -m laptime_predictor <command> [options]
"""

import sys
from laptime_predictor.cli import run

if __name__ == "__main__":
    run(sys.argv[1:])
