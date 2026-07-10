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

df_all = pd.concat(dfs, ignore_index=True)

# Convert funded_year to numeric, coercing errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Filter out rows with invalid funded_year (NaN or <= 0) and missing company_permalink
df_all = df_all[
    (df_all['funded_year'].notna()) &
    (df_all['funded_year'] > 0) &
    (df_all['company_permalink'].notna()) &
    (df_all['company_permalink'] != '')
]

# Convert raised_amount_usd to numeric, coercing errors to 0
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce').fillna(0)

# Convert funded_year and raised_amount_usd to int for grouping and output
df_all['funded_year'] = df_all['funded_year'].astype(int)
df_all['raised_amount_usd'] = df_all['raised_amount_usd'].astype(int)

grouped = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# Ensure types match target schema
grouped['company_permalink'] = grouped['company_permalink'].astype(str)
grouped['funded_year'] = grouped['funded_year'].astype(int)
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_38/target_multisource_mcts.csv", index=False)