import pandas as pd
import glob

# Get all source file paths matching the pattern
paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length1_35/training_*.csv"))

# Read all source files into dataframes
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all dataframes (UNION)
df_union = pd.concat(dfs, ignore_index=True)

# Group by 'Source Zipcode' and sum 'Counts'
df_grouped = df_union.groupby('Source Zipcode', as_index=False)['Counts'].sum()

# Cast columns to int as per target schema
df_grouped['Source Zipcode'] = df_grouped['Source Zipcode'].astype(int)
df_grouped['Counts'] = df_grouped['Counts'].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)