import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="fname")

result = joined.groupby("fname").size().reset_index(name="count_of_obs")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)