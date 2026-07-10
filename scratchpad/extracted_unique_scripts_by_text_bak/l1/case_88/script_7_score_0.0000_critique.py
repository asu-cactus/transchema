import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_88/training_*.csv"
files = sorted(glob.glob(file_pattern))

dfs = []
for f in files:
    df = pd.read_csv(f, index_col=0)
    # Ensure Price is integer type
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').astype('Int64')
    # Select columns in target schema order
    df = df[['Airline', 'Date_of_Journey', 'Source', 'Destination', 'Route', 'Dep_Time', 'Arrival_Time', 'Duration', 'Total_Stops', 'Additional_Info', 'Price']]
    dfs.append(df)

# Union all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Write to target file
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)