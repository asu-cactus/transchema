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

df = pd.concat(dfs, ignore_index=True)

df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert funded_year to numeric, coerce errors to NaN
funded_year_numeric = pd.to_numeric(df['funded_year'], errors='coerce')

# Filter out invalid funded_year values (<=1900 or >2025)
valid_year_mask = (funded_year_numeric > 1900) & (funded_year_numeric <= 2025)

df = df.loc[valid_year_mask].copy()

# Convert funded_year to int safely
df['funded_year'] = funded_year_numeric[valid_year_mask].astype(int)

# Convert raised_amount_usd to numeric, coerce errors to 0, then int
raised_amount_numeric = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0)
df['raised_amount_usd'] = raised_amount_numeric.astype(int)

# Group by company_permalink and funded_year, sum raised_amount_usd
result = df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)