import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_1/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_1/training_10.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Convert columns to numeric as needed
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0).astype(int)
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce').fillna(0).astype(int)

# First group by company_permalink and funded_year to sum raised_amount_usd per year
df_yearly = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# For each company, select the funded_year with the maximum raised_amount_usd
# This gives one row per company with the year they raised the most money and that amount
idx = df_yearly.groupby('company_permalink')['raised_amount_usd'].idxmax()
result = df_yearly.loc[idx].reset_index(drop=True)

# Ensure columns are exactly as target schema
result = result[['company_permalink', 'funded_year', 'raised_amount_usd']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)