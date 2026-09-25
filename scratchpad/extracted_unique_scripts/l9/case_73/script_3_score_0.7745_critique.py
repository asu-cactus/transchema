import pandas as pd

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
    "autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv",
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    if i == 5:
        # Source9_73_5 has 'sampled_bid_id' instead of 'bid_id', and 'message' instead of 'pii_cleaned_message'
        df = df.rename(columns={"sampled_bid_id": "bid_id"})
    # For all other sources except Source9_73_5, rename 'pii_cleaned_message' to 'message'
    if "pii_cleaned_message" in df.columns:
        df = df.rename(columns={"pii_cleaned_message": "message"})
    # Keep only 'bid_id', 'message', and 'message_timestamp' columns
    df = df[["bid_id", "message", "message_timestamp"]]
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)

# Convert 'message_timestamp' to datetime for proper max aggregation
all_data["message_timestamp"] = pd.to_datetime(all_data["message_timestamp"], utc=True, errors='coerce')

# Drop rows with NaN bid_id or message_timestamp to avoid issues
all_data = all_data.dropna(subset=["bid_id", "message_timestamp"])

# Convert bid_id to int (some may be float due to NaNs or csv reading)
all_data["bid_id"] = all_data["bid_id"].astype(int)

# For each bid_id, get the row with the max message_timestamp
idx = all_data.groupby("bid_id")["message_timestamp"].idxmax()

result = all_data.loc[idx, ["bid_id", "message"]].copy()

# Ensure types
result["bid_id"] = result["bid_id"].astype(int)
result["message"] = result["message"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)