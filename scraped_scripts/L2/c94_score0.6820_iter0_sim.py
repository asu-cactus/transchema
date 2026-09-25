import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

result = df0.groupby(df0.columns[0], as_index=False).sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)