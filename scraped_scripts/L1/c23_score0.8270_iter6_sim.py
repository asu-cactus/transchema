import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, on="customer_id")

result = joined.groupby("customer_id", as_index=False)["amount_x"].sum()
result.columns = ["customer_id", "amount"]
result["customer_id"] = result["customer_id"].astype(int)
result["amount"] = result["amount"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)