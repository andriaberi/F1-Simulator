import subprocess
from pathlib import Path
import sys
import platform

ROOT = Path(__file__).parent

# Detect virtual environment Python
def get_venv_python() -> str:
    venv_path = ROOT / "venv"  # adjust if your venv folder is named differently
    system = platform.system()

    if system == "Windows":
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Linux / macOS
        python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        print(f"Error: Could not find Python executable in virtualenv at {python_path}")
        sys.exit(1)

    return str(python_path)


def ask(prompt: str) -> str | None:
    value = input(prompt).strip()
    return value if value else None


def run_data(python_exe: str):
    year = ask("Year (2018–present, optional): ")

    race = None
    if year:
        race = ask("Race (optional): ")

    cmd = [python_exe, "-m", "lap_data"]

    if year:
        cmd += ["--year", year]
    if race:
        cmd += ["--race", race]

    subprocess.run(cmd, cwd=ROOT)


def run_predictor(python_exe: str):
    mode = ask("Mode (train | predict | evaluate | info | demo): ")

    if mode not in {"train", "predict", "evaluate", "info", "demo"}:
        print("Invalid mode")
        return

    cmd = [python_exe, "-m", "laptime_predictor", mode]

    if mode == "train":
        csv = ask("CSV file (optional): ")
        out = ask("Output model file (optional): ")

        if csv:
            cmd += ["--csv", csv]
        if out:
            cmd += ["--out", out]

    elif mode in {"predict", "evaluate"}:
        csv = ask("CSV file (optional): ")
        model = ask("Model file (optional): ")

        if csv:
            cmd += ["--csv", csv]
        if model:
            cmd += ["--model", model]

    elif mode in {"info", "demo"}:
        model = ask("Model file (optional): ")
        if model:
            cmd += ["--model", model]

    subprocess.run(cmd, cwd=ROOT)

def main():
    python_exe = get_venv_python()

    print("Jobs:")
    print("  data  -> lap_data")
    print("  pred  -> laptime_predictor")

    job = ask("Select job (data | pred): ")

    match job:
        case "data":
            run_data(python_exe)
        case "pred":
            run_predictor(python_exe)
        case _:
            print("Unknown job")


if __name__ == "__main__":
    main()