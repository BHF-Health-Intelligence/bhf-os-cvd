import pandas as pd
import os 
from glob import glob


print("Starting analysis...")
print("Current working directory:", os.getcwd())


for item in os.listdir("output"):
    print(item)


# Read all fortnightly inputs from generate_composite_datasets
composite_pattern = os.path.join("output", "composite", "attendances_*.csv.gz")
dataset_locations = sorted(glob(composite_pattern))

if not dataset_locations:
    raise FileNotFoundError(
        f"No composite datasets found matching pattern: {composite_pattern}"
    )

dataframes = [pd.read_csv(path, compression="gzip") for path in dataset_locations]
df = pd.concat(dataframes, ignore_index=True)

if "attendance_date" in df.columns:
    df["attendance_date"] = pd.to_datetime(df["attendance_date"], errors="coerce")
    df = df.sort_values("attendance_date", kind="stable")


# Save to output
df.to_csv(os.path.join("output", "analysis_results.csv"), index=False)