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
    # Select relevant columns and rename pii_cleaned_message to message
    df = df[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})
    dfs_0_4_6_7_8_9.append(df)

df_union_0_4_6_7_8_9 = pd.concat(dfs_0_4_6_7_8_9, ignore_index=True)

df_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
df_5 = df_5.rename(columns={'sampled_bid_id': 'bid_id'})
df_5 = df_5[['bid_id', 'message']]

df_all = pd.concat([df_union_0_4_6_7_8_9, df_5], ignore_index=True)

df_grouped = df_all.groupby('bid_id', as_index=False).agg({'message': lambda x: '\n\n'.join(x.dropna().astype(str))})

df_grouped['bid_id'] = df_grouped['bid_id'].astype(int)
df_grouped['message'] = df_grouped['message'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)