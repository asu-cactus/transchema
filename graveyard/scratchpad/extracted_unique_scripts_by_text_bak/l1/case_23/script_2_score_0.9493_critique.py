import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df_result = df0.groupby("customer_id", as_index=False).agg({"amount": "mean"})
df_result["customer_id"] = df_result["customer_id"].astype(int)
df_result["amount"] = df_result["amount"].astype(float)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)