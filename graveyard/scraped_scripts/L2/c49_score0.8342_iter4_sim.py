import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_49/training_1.csv", index_col=0)

result = df1.groupby('fname').agg(row_count=('ï»¿index', 'count')).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_49/target_multisource_mcts.csv", index=False)