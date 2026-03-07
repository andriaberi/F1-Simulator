def _get_compounds(weather: str) -> tuple[list[str], bool]:
    if weather == "Dry":
        return ["SOFT", "MEDIUM", "HARD"], True
    return ["INTERMEDIATE", "WET"], False


def _is_valid_compound_combo(
        combo: tuple[str, ...],
        must_use_multiple: bool,
        weather: str,
) -> bool:
    if must_use_multiple and len(set(combo)) < 2:
        return False
    if weather == "Dry" and combo[0] == "HARD":
        return False
    if combo[0] == combo[1] or combo[1] == combo[2]:
        return False
    return True
