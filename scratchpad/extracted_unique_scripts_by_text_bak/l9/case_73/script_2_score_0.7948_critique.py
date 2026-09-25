import pandas as pd

# File paths for sources 0-4 and 7-9 (same schema)
paths_0_4 = [
    "autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv",
]

paths_7_9 = [
    "autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv",
]

path_5 = "autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv"
path_6 = "autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv"

dfs = []

# Load sources 0-4 and 7-9: select bid_id and pii_cleaned_message
for p in paths_0_4 + paths_7_9:
    df = pd.read_csv(p, index_col=0)
    df = df[['bid_id', 'pii_cleaned_message']]
    dfs.append(df)

# Load source 5: rename sampled_bid_id -> bid_id, message -> pii_cleaned_message
df5 = pd.read_csv(path_5, index_col=0)
df5 = df5.rename(columns={'sampled_bid_id': 'bid_id', 'message': 'pii_cleaned_message'})
df5 = df5[['bid_id', 'pii_cleaned_message']]
dfs.append(df5)

# Load source 6: select bid_id and pii_cleaned_message
df6 = pd.read_csv(path_6, index_col=0)
df6 = df6[['bid_id', 'pii_cleaned_message']]
dfs.append(df6)

# Concatenate all dataframes (UNION)
result = pd.concat(dfs, ignore_index=True)

# Rename column to 'message' as per target schema
result = result.rename(columns={'pii_cleaned_message': 'message'})

# Group by bid_id and take the first message per bid_id
result = result.groupby('bid_id', as_index=False).agg({'message': 'first'})

# Write to output file
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)