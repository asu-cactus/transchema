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
union_df = pd.concat(dfs, ignore_index=True)

# Convert columns to numeric types
union_df['funded_year'] = pd.to_numeric(union_df['funded_year'], errors='coerce')
union_df['raised_amount_usd'] = pd.to_numeric(union_df['raised_amount_usd'], errors='coerce')

# Filter out rows with invalid or zero funded_year
filtered_df = union_df[union_df['funded_year'] > 0]

# Convert to int after filtering to avoid 0 or NaN
filtered_df['funded_year'] = filtered_df['funded_year'].astype(int)
filtered_df['raised_amount_usd'] = filtered_df['raised_amount_usd'].fillna(0).astype(int)

grouped = filtered_df.groupby(['company_permalink', 'funded_year'], as_index=False)['raised_amount_usd'].sum()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_1/target_multisource_mcts.csv", index=False)