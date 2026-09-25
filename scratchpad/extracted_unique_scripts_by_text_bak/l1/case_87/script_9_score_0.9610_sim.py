import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

grouped = df0.groupby("condition", as_index=False)["click"].mean()

grouped["condition"] = grouped["condition"].astype(int)
grouped["click"] = grouped["click"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)