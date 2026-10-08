import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_98/training_0.csv", index_col=0)

grouped = df0.groupby("MOTATE_V", as_index=False)["count"].sum()
grouped["MOTATE_V"] = grouped["MOTATE_V"].astype(str)
grouped["count"] = grouped["count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_98/target_multisource_mcts.csv", index=False)