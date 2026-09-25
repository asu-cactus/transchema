import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_87/training_0.csv", index_col=0)
result = df0.groupby("Name", as_index=False).size()
result = result[["Name"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_87/target_multisource_mcts.csv", index=False)