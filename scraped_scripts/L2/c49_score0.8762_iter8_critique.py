import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, how='left', on='fname')

result = merged.groupby('fname').size().reset_index(name='row_count')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)