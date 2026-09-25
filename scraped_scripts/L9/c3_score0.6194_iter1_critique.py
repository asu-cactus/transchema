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

# UNION all source tables
df = pd.concat(dfs, ignore_index=True)

# Select relevant columns
df = df[['company_permalink', 'funded_year', 'raised_amount_usd']]

# Convert types to match target schema
df['company_permalink'] = df['company_permalink'].astype(str)
df['funded_year'] = pd.to_numeric(df['funded_year'], errors='coerce').astype('Int64')
df['raised_amount_usd'] = pd.to_numeric(df['raised_amount_usd'], errors='coerce').fillna(0).astype('Int64')

# GROUP BY company_permalink and funded_year, SUM raised_amount_usd
df_grouped = df.groupby(['company_permalink', 'funded_year'], dropna=True, as_index=False).agg({'raised_amount_usd': 'sum'})

# Ensure types after aggregation
df_grouped['company_permalink'] = df_grouped['company_permalink'].astype(str)
df_grouped['funded_year'] = df_grouped['funded_year'].astype('Int64')
df_grouped['raised_amount_usd'] = df_grouped['raised_amount_usd'].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_3/target_multisource_mcts.csv", index=False)