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

df = pd.concat(dfs, ignore_index=True)

df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to numeric integer type, coercing errors to NaN
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce').astype('Int64')

# Convert raised_amount_usd to numeric integer, fill NaN with 0
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0).astype('Int64')

# Drop rows with NaN in group-by keys to avoid issues in grouping
df = df.dropna(subset=['company_permalink', 'funded_year'])

# Group by company_permalink and funded_year, sum raised_amount_usd
df = df.groupby(['company_permalink', 'funded_year'], as_index=False).agg({'raised_amount_usd': 'sum'})

# Convert raised_amount_usd to int (if not already)
df['raised_amount_usd'] = df['raised_amount_usd'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)