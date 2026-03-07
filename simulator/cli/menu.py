import os
import shutil

from InquirerPy import inquirer

from simulator.strategy import simulate_pitstop_strategy
from .prompts import strategy_simulator_prompt

menu_options = ["Strategy Simulator", "Exit"]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    width = shutil.get_terminal_size((80, 20)).columns

    title = "F1 SIMULATOR"
    subtitle = "Strategy * Race * Performance Simulation"

    print("=" * width)
    print()
    print(title.center(width))
    print(subtitle.center(width))
    print()
    print("=" * width)
    print()


def main_menu():
    while True:
        clear_screen()
        banner()

        choice = inquirer.select(
            message="Please Select an Option:",
            choices=menu_options,
            qmark="",
            amark=""
        ).execute()

        match choice:
            case "Strategy Simulator":
                (driver_id, team, event, weather, strategy) = strategy_simulator_prompt()
                simulate_pitstop_strategy(driver_id, team, event, weather, strategy)

                input("\nPress Enter to return to menu...")

            case "Exit":
                clear_screen()
                break


if __name__ == "__main__":
    main_menu()
