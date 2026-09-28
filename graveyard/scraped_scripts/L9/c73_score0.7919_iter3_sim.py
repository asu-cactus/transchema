import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df = df[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

result = union_df.groupby('bid_id', as_index=False).agg({'message': 'first'})

result['bid_id'] = result['bid_id'].astype(int)
result['message'] = result['message'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)