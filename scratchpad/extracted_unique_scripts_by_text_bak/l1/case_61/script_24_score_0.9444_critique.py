import pandas as pd
import glob

# Read all source files matching the pattern (assuming multiple source files exist)
# If only one source file exists, this will just read that one.
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_61/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by the leftmost columns that are keys and aggregate payment columns by mean
grouped = df_all.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'], as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to correct types as per target schema
grouped['provider_id'] = grouped['provider_id'].astype(int)
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_name'] = grouped['provider_name'].astype(str)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)