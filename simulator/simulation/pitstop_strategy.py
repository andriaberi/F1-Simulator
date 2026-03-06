from InquirerPy import inquirer

from simulator.config import *


def simulate_pitstop_strategy():
    print("")
    choice = inquirer.select(
        message="Select a Driver:",
        choices=[f"{item["name"]} - {item["team"]}" for item in ALL_DRIVERS],
        qmark="",
        amark="",
        max_height=len(DRIVERS)
    ).execute()

    driver_id = next(d["id"] for d in ALL_DRIVERS if d["name"] == choice.split(" - ")[0])
    driver_team = choice.split(" - ")[1]

    choice = inquirer.select(
        message="Select an Event:",
        choices=EVENTS,
        qmark="",
        amark="",
        max_height=len(EVENTS)
    ).execute()