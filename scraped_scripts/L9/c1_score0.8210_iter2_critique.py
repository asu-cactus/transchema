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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Convert funded_year to numeric, coercing errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Group by company_permalink, aggregate funded_year by min, raised_amount_usd by sum
grouped = df_all.groupby('company_permalink', dropna=False, as_index=False).agg({
    'funded_year': 'min',
    'raised_amount_usd': 'sum'
})

# Drop rows with missing company_permalink or funded_year after aggregation
grouped = grouped.dropna(subset=['company_permalink', 'funded_year'])

# Convert funded_year and raised_amount_usd to integer type
grouped['funded_year'] = grouped['funded_year'].astype(int)
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)