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

df = pd.concat(dfs, ignore_index=True)

df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to numeric, coercing errors to NaN, then drop rows with NaN in funded_year or company_permalink
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce')
df = df.dropna(subset=['company_permalink', 'funded_year'])

# Convert raised_amount_usd to numeric, coercing errors to NaN, fill NaN with 0
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0)

# Convert funded_year to int after dropping NaNs
df['funded_year'] = df['funded_year'].astype(int)

# Group by company_permalink and funded_year, sum raised_amount_usd
df = df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# Convert raised_amount_usd to int as in target schema
df['raised_amount_usd'] = df['raised_amount_usd'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)