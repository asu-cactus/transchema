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

df = pd.concat(dfs, ignore_index=True)

# Select only needed columns
df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to numeric integer, coercing errors to NaN, then drop NaNs
df = df[pd.to_numeric(df['funded_year'], errors='coerce').notnull()]
df['funded_year'] = df['funded_year'].astype(int)

# Convert raised_amount_usd to numeric, fill NaN with 0, convert to int
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

# Group by company_permalink and funded_year, sum raised_amount_usd
df = df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts.csv", index=False)