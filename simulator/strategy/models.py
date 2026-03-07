from dataclasses import dataclass

import datetime


@dataclass(frozen=True)
class StintConfig:
    """Immutable configuration for stint length constraints."""
    n_laps: int
    min_pct: float = 0.10
    max_pct: float = 0.45
    stop1_min_pct: float = 0.20
    stop1_max_pct: float = 0.40

    @property
    def min_stint(self) -> int:
        return max(10, int(self.n_laps * self.min_pct))

    @property
    def max_stint(self) -> int:
        return int(self.n_laps * self.max_pct)

    @property
    def stop1_min(self) -> int:
        return int(self.n_laps * self.stop1_min_pct)

    @property
    def stop1_max(self) -> int:
        return int(self.n_laps * self.stop1_max_pct)


@dataclass
class StrategyResult:
    stints: tuple[str, ...]
    stop_laps: list[int]
    stint_lengths: list[int]
    total_time: float

    COLORS = {
        "SOFT": "\033[91m", "MEDIUM": "\033[93m", "HARD": "\033[97m",
        "INTER": "\033[92m", "WET": "\033[94m",
    }
    COLORS_DARK = {
        "SOFT": "\033[31m", "MEDIUM": "\033[33m", "HARD": "\033[37m",
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def _format_time(self, seconds: float) -> str:
        td = datetime.timedelta(seconds=seconds)
        hours, remainder = divmod(int(td.total_seconds()), 3600)
        minutes, seconds_int = divmod(remainder, 60)
        ms = int(td.microseconds / 1000)
        return f"{hours:02}:{minutes:02}:{seconds_int:02}.{ms:03}"

    def display(self) -> None:
        # 1. Prepare Stint Data and calculate Table Width
        rows = []
        prev_comp = None
        is_alt = False

        for i, (comp, length) in enumerate(zip(self.stints, self.stint_lengths)):
            comp = comp.upper()
            if comp == prev_comp:
                is_alt = not is_alt
            else:
                is_alt = False

            color = self.COLORS_DARK.get(comp, "") if is_alt else self.COLORS.get(comp, "")
            lap_start = 1 if i == 0 else self.stop_laps[i - 1] + 1
            lap_end = lap_start + length - 1

            # Text parts for alignment
            stint_txt = f"STINT {i + 1}:"
            range_txt = f"LAPS {lap_start:>2}-{lap_end:<2}"
            len_txt = f"({length} LAPS)"

            visible_row = f"{stint_txt} {comp:<12}  |  {range_txt} {len_txt}"
            colored_row = f"{stint_txt} {color}{comp:<12}{self.RESET}  |  {range_txt} {len_txt}"
            rows.append((visible_row, colored_row))
            prev_comp = comp

        table_width = max(len(r[0]) for r in rows)

        # 2. Header
        print(f"\n{self.BOLD}STRATEGY REPORT{self.RESET}")
        print("—" * table_width)

        # 3. Timeline (Fixed Rounding Logic)
        print(f"{self.BOLD}TIMELINE{self.RESET}")
        total_laps = sum(self.stint_lengths)
        timeline_str = ""
        chars_used = 0
        prev_comp = None
        is_alt = False

        for i, (comp, length) in enumerate(zip(self.stints, self.stint_lengths)):
            comp = comp.upper()
            if comp == prev_comp:
                is_alt = not is_alt
            else:
                is_alt = False

            color = self.COLORS_DARK.get(comp, "") if is_alt else self.COLORS.get(comp, "")
            char = "▒" if is_alt else "█"

            # If it's the last stint, take all remaining space to avoid gaps
            if i == len(self.stints) - 1:
                bar_len = table_width - chars_used
            else:
                bar_len = round((length / total_laps) * table_width)
                chars_used += bar_len

            timeline_str += f"{color}{char * bar_len}{self.RESET}"
            prev_comp = comp

        print(timeline_str)
        print("—" * table_width)

        # 4. Body
        for _, colored_row in rows:
            print(colored_row)

        # 5. Footer (Perfectly Justified)
        print("—" * table_width)
        time_label = "TOTAL TIME:"
        time_val = self._format_time(self.total_time)
        # Calculate exactly how many spaces are needed between label and value
        gap = table_width - len(time_label) - len(time_val)
        print(f"{self.BOLD}{time_label}{' ' * gap}{time_val}{self.RESET}")
        print("—" * table_width + "\n")