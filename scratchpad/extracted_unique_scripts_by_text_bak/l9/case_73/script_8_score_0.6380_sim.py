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
        # Source9_73_5 has different schema: 'sampled_bid_id' instead of 'bid_id', and 'message' instead of 'pii_cleaned_message'
        df = df.rename(columns={"sampled_bid_id": "bid_id"})
    # For all sources except Source9_73_5, rename 'pii_cleaned_message' to 'message'
    if "pii_cleaned_message" in df.columns:
        df = df.rename(columns={"pii_cleaned_message": "message"})
    # Keep only 'bid_id' and 'message' columns
    df = df[["bid_id", "message"]]
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)

# Group by 'bid_id' and aggregate messages by concatenation separated by space
result = all_data.groupby("bid_id", as_index=False).agg({"message": lambda x: " ".join(x.dropna().astype(str))})

result["bid_id"] = result["bid_id"].astype(int)
result["message"] = result["message"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)