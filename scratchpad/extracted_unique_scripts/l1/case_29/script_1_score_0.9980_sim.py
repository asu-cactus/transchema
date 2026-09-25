import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
grouped = df0.groupby("Gender").size().reset_index(name="0")
grouped["Gender"] = grouped["Gender"].astype(str)
grouped["0"] = grouped["0"].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)