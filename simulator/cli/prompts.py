from typing import Tuple

from InquirerPy import inquirer

from simulator.config import DRIVERS, ALL_DRIVERS, EVENTS


def strategy_simulator_prompt() -> Tuple[str, str, str, str]:
    print("")
    driver = inquirer.select(
        message="Select a Driver:",
        choices=[f"{item["name"]} - {item["team"]}" for item in ALL_DRIVERS],
        qmark="",
        amark="",
        max_height=len(DRIVERS)
    ).execute()

    driver_id = next(d["id"] for d in ALL_DRIVERS if d["name"] == driver.split(" - ")[0])
    driver_team = driver.split(" - ")[1]

    event = inquirer.select(
        message="Select an Event:",
        choices=[item["event"] for item in EVENTS],
        qmark="",
        amark="",
        max_height=len(EVENTS)
    ).execute()

    weather = inquirer.select(
        message="Select a Weather:",
        choices=["Dry", "Wet"],
        qmark="",
        amark="",
    ).execute()

    print()

    return driver_id, driver_team, event, weather