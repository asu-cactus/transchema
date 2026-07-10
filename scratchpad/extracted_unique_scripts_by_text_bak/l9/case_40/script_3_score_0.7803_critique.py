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

# Convert funded_year to numeric, coercing errors to NaN (do not fill with 0 to avoid invalid years)
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Convert raised_amount_usd to numeric, coercing errors to NaN, then fill NaN with 0 and convert to int
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0).astype(int)

# Group by company_permalink only
# Aggregate funded_year by min (to get a single year per company)
# Aggregate raised_amount_usd by sum
grouped = df_all.groupby('company_permalink', dropna=False).agg({
    'funded_year': 'min',
    'raised_amount_usd': 'sum'
}).reset_index()

# Convert funded_year to int (after aggregation, NaNs may remain if no valid year)
grouped['funded_year'] = grouped['funded_year'].fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)