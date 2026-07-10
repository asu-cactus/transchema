import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_0.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_6.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_29/training_9.csv", index_col=0)

union_df = pd.concat([s2, s5, s6, s9], ignore_index=True)

merged = pd.merge(union_df, s0[['ROW_WID', 'COLLECTION_EVENTS_NUM']], on='ROW_WID', how='inner')

result = merged[['COLLECTION_EVENTS_NUM']].copy()
result['COLLECTION_EVENTS_NUM'] = result['COLLECTION_EVENTS_NUM'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts.csv", index=False)