import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)

result = df0.groupby("type").agg(a=("size", "mean"), b=("budget", "mean")).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)