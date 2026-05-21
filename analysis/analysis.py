import pandas as pd

print("Starting analysis...")

#Read in measures output file
measures_path = "output/measures_attendances.csv.gz"
df = pd.read_csv(measures_path)

#Get numerators and rename to attendances 
if "numerator" not in df.columns:
    raise ValueError(
        "Expected measures output to contain a 'numerator' column for attendance counts"
    )

df = df.rename(columns={"numerator": "attendance_count"})

#Drop denominator and ratio columns (don't need 'em)
columns_to_drop = ["ratio", "denominator"]
existing_drop_cols = [column for column in columns_to_drop if column in df.columns]
if existing_drop_cols:
    df = df.drop(columns=existing_drop_cols)

if "interval_start" in df.columns:
    df["interval_start"] = pd.to_datetime(df["interval_start"], errors="coerce")
if "interval_end" in df.columns:
    df["interval_end"] = pd.to_datetime(df["interval_end"], errors="coerce")

age_group_order = [
    "0-4",
    "5-11",
    "12-17",
    "18-25",
    "26-34",
    "35-49",
    "50-69",
    "70-79",
    "80-89",
    "90+",
]
if "age_group" in df.columns:
    df["age_group"] = pd.Categorical(
        df["age_group"], categories=age_group_order, ordered=True
    )

if "imd_quintile" in df.columns:
    df["imd_quintile"] = pd.to_numeric(df["imd_quintile"], errors="coerce")

sort_columns = []
for column in [
    "interval_start",
    "interval_end",
    "age_group",
    "ethnicity_group",
    "imd_quintile",
]:
    if column in df.columns:
        sort_columns.append(column)

if sort_columns:
    df = df.sort_values(sort_columns, kind="stable")

output_path = "output/analysis_results.csv.gz"
df.to_csv(output_path, index=False)
print(f"Saved {len(df)} grouped interval rows to {output_path}")