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

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Convert columns to numeric, coercing errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0)

# Filter out invalid funded_year values (e.g., NaN, <=1900)
df_all = df_all[df_all['funded_year'].notna() & (df_all['funded_year'] > 1900)]

# Convert funded_year and raised_amount_usd to int after filtering
df_all['funded_year'] = df_all['funded_year'].astype(int)
df_all['raised_amount_usd'] = df_all['raised_amount_usd'].astype(int)

# Group by company_permalink, aggregate min funded_year and sum raised_amount_usd
grouped = df_all.groupby('company_permalink', as_index=False).agg({
    'funded_year': 'min',
    'raised_amount_usd': 'sum'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)