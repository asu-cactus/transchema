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

df_all = pd.concat(dfs, ignore_index=True)

# Convert funded_year to numeric, coerce errors to NaN
df_all['funded_year'] = pd.to_numeric(df_all['funded_year'], errors='coerce')

# Convert raised_amount_usd to numeric, coerce errors to NaN
df_all['raised_amount_usd'] = pd.to_numeric(df_all['raised_amount_usd'], errors='coerce')

# Filter out rows with invalid funded_year or missing company_permalink
df_all = df_all[
    (df_all['funded_year'].notna()) &
    (df_all['company_permalink'].notna()) &
    (df_all['funded_year'] >= 1900) &
    (df_all['funded_year'] <= 2025)
]

# Convert funded_year and raised_amount_usd to int after filtering
df_all['funded_year'] = df_all['funded_year'].astype(int)
df_all['raised_amount_usd'] = df_all['raised_amount_usd'].fillna(0).astype(int)

grouped = df_all.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

# Ensure types match target schema
grouped['funded_year'] = grouped['funded_year'].astype(int)
grouped['raised_amount_usd'] = grouped['raised_amount_usd'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)