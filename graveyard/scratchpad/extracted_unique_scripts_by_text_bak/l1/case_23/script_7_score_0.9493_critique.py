import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)

grouped = df0.groupby("customer_id", as_index=False)["amount"].mean()
grouped["customer_id"] = grouped["customer_id"].astype(int)
grouped["amount"] = grouped["amount"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)