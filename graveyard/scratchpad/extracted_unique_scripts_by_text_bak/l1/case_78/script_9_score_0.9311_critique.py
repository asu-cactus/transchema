import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_grouped = df0.groupby("Product", as_index=False)["Price"].mean()
df_grouped["Price"] = df_grouped["Price"].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)