import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_3/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_3/training_10.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Concatenate all source tables (UNION)
df_all = pd.concat(dfs, ignore_index=True)

# Convert funded_year to integer type, coercing errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce').astype('Int64')

# Group by company_permalink and funded_year, sum raised_amount_usd
grouped = df_all.groupby(['company_permalink', 'funded_year'], dropna=False, as_index=False)['raised_amount_usd'].sum()

# Fill NaN raised_amount_usd with 0 and convert to int64
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].fillna(0).astype('int64')

# Convert funded_year to int (from Int64) and company_permalink to string explicitly
grouped['funded_year'] = grouped['funded_year'].astype('int64')
grouped['company_permalink'] = grouped['company_permalink'].astype(str)

# Write output with exact target schema and no index
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts.csv", index=False)