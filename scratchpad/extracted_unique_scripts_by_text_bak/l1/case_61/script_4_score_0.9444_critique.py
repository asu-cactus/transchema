import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

# If multiple source tables existed, we would read and concat them here:
# df1 = pd.read_csv("path_to_other_source.csv", index_col=0)
# df = pd.concat([df0, df1], ignore_index=True)
# But since only one source is given, just use df0 as df
df = df0

# Group by the key columns and aggregate averages
grouped = df.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'],
    as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to match target schema types
grouped['provider_id'] = grouped['provider_id'].astype(int)
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_name'] = grouped['provider_name'].astype(str)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

# Write output
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)