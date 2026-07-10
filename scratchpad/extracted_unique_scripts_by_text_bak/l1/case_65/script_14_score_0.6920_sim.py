import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

df_grouped = df_union.groupby("year", as_index=False).size().rename(columns={"size": "0"})
df_grouped["0"] = df_grouped["0"].astype(int)
df_grouped["year"] = df_grouped["year"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)