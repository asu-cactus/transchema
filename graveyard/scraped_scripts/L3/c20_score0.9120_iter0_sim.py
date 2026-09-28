import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_20/training_0.csv", index_col=0)
grouped = df0.groupby("SN", as_index=False)["Price"].mean()
grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_20/target_multisource_mcts.csv", index=False)