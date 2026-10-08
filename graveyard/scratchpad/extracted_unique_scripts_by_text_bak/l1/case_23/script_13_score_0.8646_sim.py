import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df0_grouped = df0.groupby("customer_id", as_index=False)["amount"].sum()
df0_grouped["customer_id"] = df0_grouped["customer_id"].astype(int)
df0_grouped["amount"] = df0_grouped["amount"].astype(float)
df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)