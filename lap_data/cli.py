import argparse
from .main import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Extract F1 lap data using FastF1")
    parser.add_argument('--year', type=int, default=None, help='Year to extract (2018-present)')
    parser.add_argument('--race', type=int, default=None, help='Race index in season schedule (1-based)')

    args = parser.parse_args()
    run_pipeline(year=args.year, race_index=args.race)

if __name__ == '__main__':
    main()
