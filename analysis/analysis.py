import pandas as pd

print("Starting analysis...")

#Read in measures output file
measures_path = "output/measures_attendances.csv.gz"
df = pd.read_csv(measures_path)

#Get numerators and rename to attendances 
if "numerator" not in df.columns:
    raise ValueError(
        "Expected measures output to contain a 'numerator' column for attendance flag"
    )

df = df.rename(columns={"numerator": "attendance_flag"})

#Drop denominator and ratio columns (don't need 'em)
# columns_to_drop = ["ratio", "denominator"]
# existing_drop_cols = [column for column in columns_to_drop if column in df.columns]
# if existing_drop_cols:
#     df = df.drop(columns=existing_drop_cols)

#Convert intervals to proper datetimes
if "interval_start" in df.columns:
    df["interval_start"] = pd.to_datetime(df["interval_start"], errors="coerce")
if "interval_end" in df.columns:
    df["interval_end"] = pd.to_datetime(df["interval_end"], errors="coerce")

#Sort columns 
if "interval_start" in df.columns:
    sort_columns = ["interval_start","interval_end","imd_quintile","age_group"]
    df = df.sort_values(sort_columns, kind="stable")

output_path = "output/analysis_results.csv.gz"
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} grouped interval rows to {output_path}")