import pandas as pd

# File paths for all sources 0-9
paths = [
    "autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv"
]

dfs = []

for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    if i == 5:
        # Source 5: rename sampled_bid_id to bid_id, keep message column
        df_sub = df.rename(columns={'sampled_bid_id': 'bid_id'})[['bid_id', 'message']]
    else:
        # Other sources: rename pii_cleaned_message to message
        df_sub = df[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})
    dfs.append(df_sub)

# Union all sources
df_all = pd.concat(dfs, ignore_index=True)

# Convert bid_id to integer type (nullable Int64)
df_all['bid_id'] = pd.to_numeric(df_all['bid_id'], errors='coerce').astype('Int64')

# Group by bid_id, aggregate message by taking first non-null message
df_final = df_all.dropna(subset=['bid_id'])  # drop rows with NaN bid_id to avoid grouping issues
df_final = df_final.groupby('bid_id', as_index=False).agg({'message': 'first'})

# Output to CSV with exact target schema and no index
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)