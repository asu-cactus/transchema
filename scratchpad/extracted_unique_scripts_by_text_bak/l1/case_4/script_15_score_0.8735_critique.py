import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)

result = df0.groupby("fname").size().reset_index(name="count_of_obs")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)