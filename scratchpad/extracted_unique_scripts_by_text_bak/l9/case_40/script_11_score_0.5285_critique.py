import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_40/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables (concatenate)
df_all = pd.concat(dfs, ignore_index=True)

# Select only target columns
df_all = df_all[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to integer, coercing errors to NaN then fill with 0 and convert to int
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce').fillna(0).astype(int)

# Convert raised_amount_usd to integer, coercing errors to NaN then fill with 0 and convert to int
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

# GROUP BY company_permalink and funded_year, sum raised_amount_usd
result = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)