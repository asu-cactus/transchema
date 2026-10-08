import pandas as pd

# Read all source tables (assuming 5 source files named training_0.csv to training_4.csv)
dfs = []
for i in range(5):
    df = pd.read_csv(f"autopipeline-benchmarks/github-pipelines/length1_6/training_{i}.csv", index_col=0)
    dfs.append(df)

# UNION all source tables by concatenation
df_all = pd.concat(dfs, ignore_index=True)

# Group by the leftmost unique keys and aggregate averages of payment columns
grouped = df_all.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'], as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Cast columns to target schema types
grouped['provider_id'] = grouped['provider_id'].astype(int)
grouped['provider_zip_code'] = grouped['provider_zip_code'].astype(int)
grouped['provider_name'] = grouped['provider_name'].astype(str)
grouped['average_covered_charges'] = grouped['average_covered_charges'].astype(float)
grouped['average_total_payments'] = grouped['average_total_payments'].astype(float)
grouped['average_medicare_payments'] = grouped['average_medicare_payments'].astype(float)

# Write output to target file
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)