import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_89/training_0.csv", index_col=0)

result = df0.groupby("city", as_index=False)["fare"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_89/target_multisource_mcts.csv", index=False)