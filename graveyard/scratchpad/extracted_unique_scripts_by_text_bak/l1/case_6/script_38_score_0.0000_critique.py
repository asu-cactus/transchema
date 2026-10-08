import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_6/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_6/training_5.csv"
]

dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

# Select only needed columns
cols = [
    'provider_id',
    'provider_name',
    'provider_zip_code',
    'average_covered_charges',
    'average_total_payments',
    'average_medicare_payments'
]
df = union_df[cols].copy()

# Convert types to match target schema
df['provider_id'] = df['provider_id'].astype('Int64')
df['provider_name'] = df['provider_name'].astype(str)
df['provider_zip_code'] = df['provider_zip_code'].astype('Int64')
df['average_covered_charges'] = df['average_covered_charges'].astype(float)
df['average_total_payments'] = df['average_total_payments'].astype(float)
df['average_medicare_payments'] = df['average_medicare_payments'].astype(float)

# Group by provider_id, provider_name, provider_zip_code and aggregate averages by mean
result = df.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'],
    dropna=False,
    as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_6/target_multisource_mcts.csv", index=False)