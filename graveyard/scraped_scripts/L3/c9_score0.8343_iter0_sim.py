import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_9/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_9/training_1.csv", index_col=0)

df1_grouped = df1.groupby("park_name", as_index=False)["observations"].sum()

df1_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_9/target_multisource_mcts.csv", index=False)