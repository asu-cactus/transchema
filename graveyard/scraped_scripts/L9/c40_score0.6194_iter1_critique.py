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

# Convert funded_year to numeric, coercing errors to NaN, then drop NaNs to avoid grouping on invalid years
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce')
df = df.dropna(subset=['funded_year'])

# Convert raised_amount_usd to numeric, coercing errors to NaN, fill NaN with 0
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0)

# Group by company_permalink and funded_year, sum raised_amount_usd
df_grouped = df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# Convert types to match target schema: company_permalink (string), funded_year (int), raised_amount_usd (int)
df_grouped['funded_year'] = df_grouped['funded_year'].astype(int)
df_grouped['raised_amount_usd'] = df_grouped['raised_amount_usd'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_40/target_multisource_mcts.csv", index=False)