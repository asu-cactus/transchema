import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)
df_grouped = df0.groupby("condition", as_index=False)["click"].sum()
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)