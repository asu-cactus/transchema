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
for path in paths:
    df = pd.read_csv(path, index_col=0)
    if 'sampled_bid_id' in df.columns:
        df = df.rename(columns={'sampled_bid_id': 'bid_id', 'message': 'pii_cleaned_message'})
    # For sources with 'message' column, rename to 'pii_cleaned_message' to unify
    if 'message' in df.columns and 'pii_cleaned_message' not in df.columns:
        df = df.rename(columns={'message': 'pii_cleaned_message'})
    # Keep only bid_id and pii_cleaned_message columns
    df = df[['bid_id', 'pii_cleaned_message']]
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)

# Group by bid_id, aggregate messages by concatenation separated by space
grouped = all_data.groupby('bid_id', as_index=False).agg({'pii_cleaned_message': lambda x: ' '.join(x.dropna().astype(str))})

grouped = grouped.rename(columns={'pii_cleaned_message': 'message'})

grouped['bid_id'] = grouped['bid_id'].astype(int)
grouped['message'] = grouped['message'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)