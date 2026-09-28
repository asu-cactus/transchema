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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all = df_all[['company_permalink', 'funded_year', 'raised_amount_usd']]

df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce')

# Filter out invalid funded_year values (keep reasonable years)
df_all = df_all[(df_all['funded_year'] >= 1900) & (df_all['funded_year'] <= 2100)]

# Convert to int after filtering
df_all['funded_year'] = df_all['funded_year'].astype(int)

# Fill NaN raised_amount_usd with 0 and convert to int
df_all['raised_amount_usd'] = df_all['raised_amount_usd'].fillna(0).astype(int)

result = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts.csv", index=False)