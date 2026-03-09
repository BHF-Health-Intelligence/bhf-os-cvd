import pandas as pd
import os 


#Read input data
dataset_location=os.path.join("output","dataset.csv.gz") 
df = pd.read_csv(dataset_location, compression='gzip')


#Save to output 
df.head().to_csv(os.path.join("output", "analysis_results.csv"), index=False)
