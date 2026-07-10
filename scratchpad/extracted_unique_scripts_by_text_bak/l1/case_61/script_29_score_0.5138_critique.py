import pandas as pd
from functools import reduce

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_61/training_9.csv",
]

# Columns to keep and their types
cols = ['provider_id', 'provider_name', 'provider_zip_code', 
        'average_covered_charges', 'average_total_payments', 'average_medicare_payments']

# Read all source tables
dfs = []
for f in source_files:
    df = pd.read_csv(f, index_col=0)
    df = df[cols].copy()
    # Ensure correct types
    df['provider_id'] = df['provider_id'].astype(int)
    df['provider_zip_code'] = df['provider_zip_code'].astype(int)
    df['provider_name'] = df['provider_name'].astype(str)
    df['average_covered_charges'] = df['average_covered_charges'].astype(float)
    df['average_total_payments'] = df['average_total_payments'].astype(float)
    df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)
    dfs.append(df)

# Join all dataframes on provider_id using inner join to keep only providers present in all sources
# Since provider_name and provider_zip_code should be consistent, we keep them from the first df
# We'll join only on provider_id, then merge provider_name and provider_zip_code from the first df
# To avoid column duplication, join only on provider_id and keep other columns from first df

# Start with first df as base
base_df = dfs[0][['provider_id', 'provider_name', 'provider_zip_code']].drop_duplicates(subset=['provider_id'])

# Concatenate all average columns from all dfs keyed by provider_id
# For each df, keep provider_id and the 3 average columns, rename average columns to unique names to avoid collision
avg_cols = ['average_covered_charges', 'average_total_payments', 'average_medicare_payments']

# Prepare list of dfs with only provider_id and average columns, rename average columns to unique names
avg_dfs = []
for i, df in enumerate(dfs):
    temp = df[['provider_id'] + avg_cols].copy()
    temp = temp.rename(columns={
        'average_covered_charges': f'average_covered_charges_{i}',
        'average_total_payments': f'average_total_payments_{i}',
        'average_medicare_payments': f'average_medicare_payments_{i}',
    })
    avg_dfs.append(temp)

# Merge all avg_dfs on provider_id
merged_avg = reduce(lambda left, right: pd.merge(left, right, on='provider_id', how='inner'), avg_dfs)

# Now compute mean of all average columns across all sources
merged_avg['average_covered_charges'] = merged_avg[[f'average_covered_charges_{i}' for i in range(len(dfs))]].mean(axis=1)
merged_avg['average_total_payments'] = merged_avg[[f'average_total_payments_{i}' for i in range(len(dfs))]].mean(axis=1)
merged_avg['average_medicare_payments'] = merged_avg[[f'average_medicare_payments_{i}' for i in range(len(dfs))]].mean(axis=1)

# Keep only provider_id and the aggregated average columns
aggregated = merged_avg[['provider_id', 'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Join aggregated averages with base_df to get provider_name and provider_zip_code
final_df = pd.merge(base_df, aggregated, on='provider_id', how='inner')

# Reorder columns to match target schema
final_df = final_df[['provider_id', 'provider_name', 'provider_zip_code', 
                     'average_covered_charges', 'average_total_payments', 'average_medicare_payments']]

# Write to output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)