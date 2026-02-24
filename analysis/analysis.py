import pandas as pd
import os 


# this_dir=os.getcwd()

# dataset_location=os.path.join(this_dir,"output", "dataset.csv.gz") 

# print("You are in:", this_dir)


# # working_dir = os.getcwd()
# print(f"Containing: {os.listdir(this_dir)}")



# os.chdir()




print(os.path.exists("./output/dataset.csv.gz"))



# df = pd.read_csv(dataset_location, compression='gzip')
# df.head().to_csv(os.path.join(this_dir, "output", "analysis_results.csv"), index=False)