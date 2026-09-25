import pandas as pd

# List all source files (assuming 6 source files named training_0.csv to training_5.csv)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_5.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by the key columns and aggregate averages
agg_df = df_all.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'], as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to correct types matching target schema
agg_df['provider_id'] = agg_df['provider_id'].astype(int)
agg_df['provider_zip_code'] = agg_df['provider_zip_code'].astype(int)
agg_df['provider_name'] = agg_df['provider_name'].astype(str)
agg_df['average_covered_charges'] = agg_df['average_covered_charges'].astype(float)
agg_df['average_total_payments'] = agg_df['average_total_payments'].astype(float)
agg_df['average_medicare_payments'] = agg_df['average_medicare_payments'].astype(float)

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)