import os
from InquirerPy import inquirer
from simulator.simulation import simulate_pitstop_strategy

menu_options = ["Strategy Simulator", "Exit"]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("===================================================")
    print("")
    print("               Welcome to F1 Simulator             ")
    print("")
    print("===================================================")
    print("")

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
                simulate_pitstop_strategy()
                input("\nPress Enter to return to menu...")

            case "Exit":
                clear_screen()
                break

if __name__ == "__main__":
    main_menu()