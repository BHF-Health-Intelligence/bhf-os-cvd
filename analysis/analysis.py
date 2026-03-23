import pandas as pd
import os 


print("Starting analysis...")
print("Current working directory:", os.getcwd())


for item in os.listdir('output'):
    print(item)


# Read input data from generate_dataset
dataset_location=os.path.join("output","dataset.csv.gz") 
df = pd.read_csv(dataset_location, compression='gzip')


# Save to output 
df.head(100).to_csv(os.path.join("output", "analysis_results.csv"), index=False)