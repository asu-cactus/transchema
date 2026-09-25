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

df_all = pd.concat(dfs, ignore_index=True)

df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0)

# Group by company_permalink only
grouped = df_all.groupby('company_permalink', dropna=False, as_index=False).agg({
    'funded_year': 'max',  # latest funded_year per company
    'raised_amount_usd': 'sum'  # total raised amount per company
})

# Convert to int as target schema requires integer types
grouped['funded_year'] = grouped['funded_year'].fillna(0).astype(int)
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)