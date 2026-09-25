import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_38/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_38/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables (they have the same schema)
df_all = pd.concat(dfs, ignore_index=True)

# Select only needed columns
df_all = df_all[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to numeric, coerce errors to NaN, then drop rows with NaN in funded_year
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')
df_all = df_all.dropna(subset=['funded_year'])

# Convert raised_amount_usd to numeric, coerce errors to NaN, fill NaN with 0
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0)

# Group by company_permalink, aggregate funded_year by max, raised_amount_usd by sum
result = df_all.groupby('company_permalink', as_index=False).agg({
    'funded_year': 'max',
    'raised_amount_usd': 'sum'
})

# Convert to integer as per target schema
result['funded_year'] = result['funded_year'].astype(int)
result['raised_amount_usd'] = result['raised_amount_usd'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)