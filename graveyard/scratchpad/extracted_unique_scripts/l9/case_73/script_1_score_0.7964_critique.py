import pandas as pd

# File paths for sources 0-4,6-9 (same schema)
paths_0_4_6_7_8_9 = [
    "autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv"
]

dfs_0_4_6_7_8_9 = []
for path in paths_0_4_6_7_8_9:
    df = pd.read_csv(path, index_col=0)
    # Rename pii_cleaned_message to message for uniformity
    if 'pii_cleaned_message' in df.columns:
        df = df.rename(columns={'pii_cleaned_message': 'message'})
    # Keep only needed columns including message_timestamp for sorting
    df = df[['bid_id', 'message_timestamp', 'message']]
    dfs_0_4_6_7_8_9.append(df)

df_union_0_9 = pd.concat(dfs_0_4_6_7_8_9, ignore_index=True)

# Load source 5, rename sampled_bid_id to bid_id, keep message_timestamp if exists
df_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
df_5 = df_5.rename(columns={'sampled_bid_id': 'bid_id'})
# Source 5 has 'message' and 'message_timestamp'
df_5 = df_5[['bid_id', 'message_timestamp', 'message']]

# Combine all sources
df_all = pd.concat([df_union_0_9, df_5], ignore_index=True)

# Convert bid_id to integer type (nullable Int64)
df_all['bid_id'] = pd.to_numeric(df_all['bid_id'], errors='coerce').astype('Int64')

# Convert message_timestamp to datetime for sorting
df_all['message_timestamp'] = pd.to_datetime(df_all['message_timestamp'], errors='coerce')

# Sort by bid_id and message_timestamp ascending to get earliest message first
df_all = df_all.sort_values(['bid_id', 'message_timestamp'], ascending=[True, True])

# Drop duplicates keeping first message per bid_id
df_result = df_all.drop_duplicates(subset=['bid_id'], keep='first')

# Select only bid_id and message columns as per target schema
df_result = df_result[['bid_id', 'message']]

# Write to CSV without index
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)