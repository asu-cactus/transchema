import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_0.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_9.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_35/training_4.csv", index_col=0)

union_0_8_9 = pd.concat([df0, df8, df9], ignore_index=True)

result = pd.merge(union_0_8_9[['ROW_WID']], df4, on='ROW_WID', how='inner')

result = result[['TECHSUPPORT_NUM']].copy()
result['TECHSUPPORT_NUM'] = result['TECHSUPPORT_NUM'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_35/target_multisource_mcts.csv", index=False)