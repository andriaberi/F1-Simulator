"""
Command-line interface for laptime_predictor.

Commands
--------
    python -m laptime_predictor train    --csv data/all.csv --out train/model.pkl
    python -m laptime_predictor predict  --csv data/all.csv --model train/model.pkl
    python -m laptime_predictor evaluate --csv data/all.csv --model train/model.pkl
    python -m laptime_predictor info     --model train/model.pkl
    python -m laptime_predictor demo     --model train/model.pkl
"""

import argparse
import sys

from laptime_predictor.config import DEFAULT_MODEL_PATH, DEFAULT_DATA_PATH
from laptime_predictor.main import train, predict, evaluate
from laptime_predictor.predictor import F1LapPredictor

# Hardcoded demo scenarios
DEMO_SCENARIOS = [
    # (Driver,              Team,                Event, Compound, TyreLife, n_laps)
      ( "VER", "Red Bull Racing", "Bahrain Grand Prix", "MEDIUM",        1,      5),
      ( "HAM",        "Mercedes", "British Grand Prix",   "SOFT",        8,      5),
      ( "LEC",         "Ferrari",  "Monaco Grand Prix",   "SOFT",        1,      5),
      ( "NOR",         "McLaren", "Italian Grand Prix",   "HARD",       15,      5),
      ( "ALO",    "Aston Martin", "Spanish Grand Prix", "MEDIUM",       10,      5),
]


# Helpers
def _fmt(seconds: float) -> str:
    """Convert seconds to m:ss.ms string, e.g. 89.743 → 1:29.743"""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


def _run_info(predictor: F1LapPredictor) -> None:
    print("\nMODEL SUMMARY")
    print("─" * 60)
    print(f"Train MAE    {predictor.train_mae_:.3f} s")
    print(f"Test  MAE    {predictor.test_mae_:.3f} s")

    # Drivers
    drivers = predictor.known_drivers()
    print(f"\n\nDRIVERS ({len(drivers)})")
    print("─" * 60)
    for i in range(0, len(drivers), 6):
        print(" ".join(f"{d:<5}" for d in drivers[i:i + 6]))

    # Events
    events = predictor.known_events()
    print(f"\n\nEVENTS ({len(events)})")
    print("─" * 60)
    for e in events:
        print(e)

    # Compounds
    compounds = predictor.known_compounds()
    print("\n\nCOMPOUNDS")
    print("─" * 60)
    print(" ".join(f"{c:<7}" for c in compounds))

    # Feature importance
    print("\n\nTOP FEATURES (by importance)")
    print("─" * 60)
    max_score = predictor.feature_importance_.max()

    for feat, score in predictor.feature_importance(top_n=10).items():
        bar_len = int((score / max_score) * 30)
        bar = "█" * bar_len
        print(f"{feat:<35} {bar}")


def _run_demo(predictor: F1LapPredictor) -> None:
    print("\nSIMULATION RESULTS")
    print("─" * 72)
    print(
        f"{'Driver':<7}"
        f"{'Event':<21}"
        f"{'Cmpd':<6}"
        f"{'Tyre':>6}"
        f"{'Lap(s)':>10}"
        f"{'Time':>11}"
    )
    print(
        f"{'──────':<7}"
        f"{'───────────────────':<21}"
        f"{'────':<6}"
        f"{'────':>6}"
        f"{'───────':>10}"
        f"{'───────':>11}"
    )

    for driver, team, event, compound, tyre_life, n_laps in DEMO_SCENARIOS:
        result = predictor.simulate(
            Driver=driver,
            Team=team,
            Event=event,
            Compound=compound,
            TyreLife=tyre_life,
            n_laps=n_laps,
            verbose=False,
        )

        first = True
        for age, laptime in result.items():
            if first:
                print(
                    f"{driver:<7}"
                    f"{event.replace(' Grand Prix',' GP'):<21}"
                    f"{compound[:3]:<6}"
                    f"{age:>6}"
                    f"{laptime:>10.3f}"
                    f"{_fmt(laptime):>11}"
                )
                first = False
            else:
                print(
                    f"{'':<7}"
                    f"{'':<21}"
                    f"{'':<6}"
                    f"{age:>6}"
                    f"{laptime:>10.3f}"
                    f"{_fmt(laptime):>11}"
                )

        print()


# Parser
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="laptime_predictor",
        description="F1 lap time predictor — train, predict, evaluate, info, demo.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # --- train ---
    p_train = sub.add_parser("train", help="Train and save a new model.")
    p_train.add_argument("--csv",     default=DEFAULT_DATA_PATH,  help=f"Training CSV (default: {DEFAULT_DATA_PATH})")
    p_train.add_argument("--out",     default=DEFAULT_MODEL_PATH, help=f"Output model path (default: {DEFAULT_MODEL_PATH})")
    p_train.add_argument("--verbose", type=int, default=200,      help="LightGBM log frequency (default: 200, 0=silent)")

    # --- predict ---
    p_pred = sub.add_parser("predict", help="Run predictions using a saved model.")
    p_pred.add_argument("--csv",   default=DEFAULT_DATA_PATH,  help=f"Input CSV (default: {DEFAULT_DATA_PATH})")
    p_pred.add_argument("--model", default=DEFAULT_MODEL_PATH, help=f"Model path (default: {DEFAULT_MODEL_PATH})")
    p_pred.add_argument("--out",   default=None,               help="Optional CSV path to save predictions")

    # --- evaluate ---
    p_eval = sub.add_parser("evaluate", help="Evaluate MAE of a saved model.")
    p_eval.add_argument("--csv",   default=DEFAULT_DATA_PATH,  help=f"Input CSV (default: {DEFAULT_DATA_PATH})")
    p_eval.add_argument("--model", default=DEFAULT_MODEL_PATH, help=f"Model path (default: {DEFAULT_MODEL_PATH})")

    # --- info ---
    p_info = sub.add_parser("info", help="Print model stats, known drivers/events/compounds, and feature importance.")
    p_info.add_argument("--model", default=DEFAULT_MODEL_PATH, help=f"Model path (default: {DEFAULT_MODEL_PATH})")

    # --- demo ---
    p_demo = sub.add_parser("demo", help="Run hardcoded simulation scenarios to verify the model.")
    p_demo.add_argument("--model", default=DEFAULT_MODEL_PATH, help=f"Model path (default: {DEFAULT_MODEL_PATH})")

    return parser


# Entry point
def run(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "train":
        predictor = train(data_path=args.csv, save_path=args.out, verbose=args.verbose)
        print("\nTop 10 features:")
        print(predictor.feature_importance(top_n=10).to_string())

    elif args.command == "predict":
        preds = predict(data_path=args.csv, model_path=args.model)
        print(preds.to_string())
        if args.out:
            preds.to_csv(args.out, index=True)
            print(f"\nPredictions saved → {args.out}")

    elif args.command == "evaluate":
        evaluate(data_path=args.csv, model_path=args.model)

    elif args.command == "info":
        predictor = F1LapPredictor.load(args.model)
        _run_info(predictor)

    elif args.command == "demo":
        predictor = F1LapPredictor.load(args.model)
        _run_demo(predictor)


if __name__ == "__main__":
    run(sys.argv[1:])