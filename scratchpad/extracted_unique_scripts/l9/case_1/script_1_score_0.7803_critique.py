import pandas as pd
import numpy as np

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

# Convert funded_year to numeric, coerce errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Filter out invalid funded_year values (e.g., <= 1900 or > current year + some margin)
# Since target examples have years like 2013, 2011, 2010, we keep reasonable years only
valid_year_mask = (df_all['funded_year'] >= 1900) & (df_all['funded_year'] <= 2100)
df_all.loc[~valid_year_mask, 'funded_year'] = np.nan

# Convert raised_amount_usd to numeric, coerce errors to 0
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0)

# Group by company_permalink
grouped = df_all.groupby('company_permalink', as_index=False).agg({
    'funded_year': 'min',  # take earliest valid funded_year per company
    'raised_amount_usd': 'sum'
})

# Convert funded_year and raised_amount_usd to int as per target schema
grouped['funded_year'] = grouped['funded_year'].fillna(0).astype(int)
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)