import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df_grouped = df0.groupby("PRODUCTLINE", as_index=False)["SALES"].sum()
df_grouped["PRODUCTLINE"] = df_grouped["PRODUCTLINE"].astype(str)
df_grouped["SALES"] = df_grouped["SALES"].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)