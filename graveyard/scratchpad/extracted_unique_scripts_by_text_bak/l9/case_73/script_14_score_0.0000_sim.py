import pandas as pd

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
    dfs_0_4_6_7_8_9.append(df[['bid_id', 'message']])

df_union_0_9 = pd.concat(dfs_0_4_6_7_8_9, ignore_index=True)

df_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
df_5 = df_5.rename(columns={'sampled_bid_id': 'bid_id'})
df_5 = df_5[['bid_id', 'message']]

df_all = pd.concat([df_union_0_9, df_5], ignore_index=True)

df_all['bid_id'] = pd.to_numeric(df_all['bid_id'], errors='coerce').astype('Int64')

df_result = df_all[['bid_id', 'message']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)