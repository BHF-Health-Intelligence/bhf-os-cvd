import pandas as pd
import os 



print("Starting analysis...")

print("Current working directory:", os.getcwd())


# for item in os.listdir('output'):
#     print(item)



#Read input data
dataset_location=os.path.join("analysis","dataset.csv.gz") 
df = pd.read_csv(dataset_location, compression='gzip')


#Save to output 
df.head().to_csv(os.path.join("output", "analysis_results.csv"), index=False)