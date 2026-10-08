import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)
grouped = df0.groupby("type", as_index=False)["driver_count"].sum()
max_driver_count = grouped["driver_count"].max()
result = grouped[grouped["driver_count"] == max_driver_count]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)