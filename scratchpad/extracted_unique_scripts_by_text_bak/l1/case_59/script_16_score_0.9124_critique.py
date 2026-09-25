import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_59/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = []
for f in files:
    df = pd.read_csv(f, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Drop rows with missing PRODUCTLINE or SALES
df_all = df_all.dropna(subset=['PRODUCTLINE', 'SALES'])

# Convert SALES to numeric (coerce errors to NaN, then drop)
df_all['SALES'] = pd.to_numeric(df_all['SALES'], errors='coerce')
df_all = df_all.dropna(subset=['SALES'])

# Group by PRODUCTLINE and sum SALES
result = df_all.groupby('PRODUCTLINE', as_index=False)['SALES'].sum()

# Write output with exact target schema and column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)