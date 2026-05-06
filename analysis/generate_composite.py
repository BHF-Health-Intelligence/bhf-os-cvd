from datetime import date, timedelta
from pathlib import Path
import os
import subprocess


GLOBAL_START = date.fromisoformat("2017-04-01")
GLOBAL_END = date.fromisoformat("2025-05-01")
WINDOW_DAYS = 14
OUTPUT_DIR = Path("output/composite")


def iter_fortnights(start: date, end: date):
    current = start
    while current <= end:
        period_end = min(current + timedelta(days=WINDOW_DAYS - 1), end)
        yield current, period_end
        current = period_end + timedelta(days=1)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for period_start, period_end in iter_fortnights(GLOBAL_START, GLOBAL_END):
        filename = (
            f"attendances_{period_start.isoformat()}_{period_end.isoformat()}.csv.gz"
        )
        output_path = OUTPUT_DIR / filename

        env = os.environ.copy()
        env["PERIOD_START"] = period_start.isoformat()
        env["PERIOD_END"] = period_end.isoformat()

        command = [
            "ehrql",
            "generate-dataset",
            "analysis/dataset_definition.py",
            "--output",
            str(output_path),
        ]

        print(
            f"Generating {output_path} for window {env['PERIOD_START']} to {env['PERIOD_END']}"
        )
        subprocess.run(command, check=True, env=env)


if __name__ == "__main__":
    main()
