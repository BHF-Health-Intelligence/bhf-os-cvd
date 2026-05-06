import os
from glob import glob

import pandas as pd

print("Starting analysis...")
print("Current working directory:", os.getcwd())

# Read all weekly outputs produced by the generate_dataset_week_N actions
composite_pattern = os.path.join("output", "composite", "output_dataset_week_*.csv.gz")
dataset_locations = sorted(
    glob(composite_pattern),
    key=lambda p: int(
        os.path.basename(p)
        .replace("output_dataset_week_", "")
        .replace(".csv.gz", "")
    ),
)

if not dataset_locations:
    raise FileNotFoundError(
        f"No composite datasets found matching: {composite_pattern}"
    )

print(f"Concatenating {len(dataset_locations)} weekly files...")
dataframes = [pd.read_csv(path) for path in dataset_locations]
df = pd.concat(dataframes, ignore_index=True)

if "attendance_date" in df.columns:
    df["attendance_date"] = pd.to_datetime(df["attendance_date"], errors="coerce")
    df = df.sort_values("attendance_date", kind="stable")

output_path = os.path.join("output", "analysis_results.csv.gz")
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} rows to {output_path}")