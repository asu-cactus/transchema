import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_1.csv", index_col=0)

grouped = df1.groupby('city', as_index=False)['fare'].mean()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_30/target_multisource_mcts.csv", index=False)