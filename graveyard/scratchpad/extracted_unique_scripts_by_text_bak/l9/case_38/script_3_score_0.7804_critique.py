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

# Convert funded_year to numeric, coerce errors to NaN, then drop rows with NaN in funded_year
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce')
df = df.dropna(subset=['funded_year'])

# Convert to int after dropping NaNs
df['funded_year'] = df['funded_year'].astype(int)

# Convert raised_amount_usd to numeric, coerce errors to NaN, fill NaN with 0, convert to int
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

# Group by company_permalink, aggregate funded_year by max, raised_amount_usd by sum
result = df.groupby('company_permalink', as_index=False).agg({
    'funded_year': 'max',
    'raised_amount_usd': 'sum'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)