import pandas as pd

# Paths for all 10 sources
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
        # Source 5 schema: sampled_bid_id, message_timestamp, message_sender, message, category, agent_group
        # Rename sampled_bid_id to bid_id, keep message_timestamp and message
        df = df.rename(columns={'sampled_bid_id': 'bid_id'})
        df = df[['bid_id', 'message_timestamp', 'message']]
    else:
        # Other sources: bid_id, bid_id_header, message_timestamp, message_sender, pii_cleaned_message, ...
        # Select bid_id, message_timestamp, pii_cleaned_message as message
        df = df[['bid_id', 'message_timestamp', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})
    dfs.append(df)

# Concatenate all sources
df_all = pd.concat(dfs, ignore_index=True)

# Convert message_timestamp to datetime for proper ordering
df_all['message_timestamp'] = pd.to_datetime(df_all['message_timestamp'], utc=True, errors='coerce')

# Drop rows with NaN bid_id or message_timestamp or message (to avoid issues)
df_all = df_all.dropna(subset=['bid_id', 'message_timestamp', 'message'])

# Convert bid_id to int (some may be float due to NaNs before)
df_all['bid_id'] = df_all['bid_id'].astype(int)

# For each bid_id, pick the message with the latest message_timestamp
idx = df_all.groupby('bid_id')['message_timestamp'].idxmax()
df_latest = df_all.loc[idx, ['bid_id', 'message']]

# Reset index
df_latest = df_latest.reset_index(drop=True)

# Write output
df_latest.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)