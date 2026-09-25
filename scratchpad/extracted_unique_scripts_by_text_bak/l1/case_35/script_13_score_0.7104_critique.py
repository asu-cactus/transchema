import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_paths = sorted(glob.glob("autopipeline-benchmarks/github-pipelines/length1_35/training_*.csv"))

# Read and union all source tables
dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'Source Zipcode' and sum 'Counts'
result = df_all.groupby('Source Zipcode', as_index=False)['Counts'].sum()

# Ensure correct types
result['Source Zipcode'] = result['Source Zipcode'].astype(int)
result['Counts'] = result['Counts'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)