import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)

result = df0.groupby("customer_id", as_index=False)["amount"].sum()
result["customer_id"] = result["customer_id"].astype(int)
result["amount"] = result["amount"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)