import pandas as pd
import glob

# Read all source CSV files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_6/training_*.csv"
files = glob.glob(file_pattern)

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by provider_id and aggregate
grouped = df_all.groupby('provider_id').agg({
    'provider_name': 'first',
    'provider_zip_code': 'first',
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
}).reset_index()

# Cast columns to target schema types
grouped['provider_id'] = grouped['provider_id'].astype(int)
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_name'] = grouped['provider_name'].astype(str)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)