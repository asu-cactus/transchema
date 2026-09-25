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

df_all = pd.concat(dfs, ignore_index=True)

# Convert funded_year to numeric, coerce errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Filter valid funded_year values (reasonable year range)
df_all = df_all[(df_all['funded_year'] >= 1900) & (df_all['funded_year'] <= 2025)]

# Convert funded_year to int after filtering
df_all['funded_year'] = df_all['funded_year'].astype(int)

# Convert raised_amount_usd to numeric, coerce errors to 0, then int
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

# Group by company_permalink and funded_year, sum raised_amount_usd
result = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)