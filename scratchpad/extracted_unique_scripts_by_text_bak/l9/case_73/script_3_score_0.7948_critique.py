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
        # Source9_73_5 has 'sampled_bid_id' and 'message' columns instead of 'bid_id' and 'pii_cleaned_message'
        df = df.rename(columns={"sampled_bid_id": "bid_id"})
        df = df[["bid_id", "message"]]
    elif i == 6:
        # Source9_73_6 has extra columns '5040' and '100.00%', use 'pii_cleaned_message' as message
        df = df.rename(columns={"pii_cleaned_message": "message"})
        df = df[["bid_id", "message"]]
    else:
        # Other sources use 'pii_cleaned_message' as message
        df = df.rename(columns={"pii_cleaned_message": "message"})
        df = df[["bid_id", "message"]]
    dfs.append(df)

# Union all dataframes
result = pd.concat(dfs, ignore_index=True)

# Convert bid_id to integer type (nullable Int64)
result["bid_id"] = pd.to_numeric(result["bid_id"], errors="coerce").astype("Int64")

# Group by bid_id and aggregate message by taking the first non-null message per bid_id
result = result.dropna(subset=["bid_id"])  # drop rows with NaN bid_id to avoid grouping issues
result = result.groupby("bid_id", as_index=False).agg({"message": "first"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)