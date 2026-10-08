import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_paths = glob.glob("autopipeline-benchmarks/github-pipelines/length1_88/training_*.csv")

# Read and concatenate all source tables
df_list = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df = pd.concat(df_list, ignore_index=True)

# Convert Price to integer safely
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).astype(int)

# Set correct dtypes for string columns
df = df.astype({
    'Airline': 'string',
    'Date_of_Journey': 'string',
    'Source': 'string',
    'Destination': 'string',
    'Route': 'string',
    'Dep_Time': 'string',
    'Arrival_Time': 'string',
    'Duration': 'string',
    'Total_Stops': 'string',
    'Additional_Info': 'string'
})

# Write the final output
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_88/target_multisource_mcts.csv", index=False)