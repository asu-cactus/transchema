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
    # For these sources, the message column is 'pii_cleaned_message'
    df_sub = df[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})
    dfs_0_4_6_7_8_9.append(df_sub)

df_union_0_4_6_7_8_9 = pd.concat(dfs_0_4_6_7_8_9, ignore_index=True)

df_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
df_5_sub = df_5.rename(columns={'sampled_bid_id': 'bid_id'})[['bid_id', 'message']]

df_final = pd.concat([df_union_0_4_6_7_8_9, df_5_sub], ignore_index=True)

df_final['bid_id'] = pd.to_numeric(df_final['bid_id'], errors='coerce').astype('Int64')

df_final = df_final[['bid_id', 'message']]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)