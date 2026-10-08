import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df0_grouped = df0.groupby("PRODUCTLINE", dropna=False, as_index=False)["SALES"].sum()
df0_grouped["SALES"] = df0_grouped["SALES"].astype(float)
df0_grouped["PRODUCTLINE"] = df0_grouped["PRODUCTLINE"].astype(str)
df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)