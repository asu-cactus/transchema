import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

j0 = pd.merge(s1, s4, on="Ship_id", how="inner")
j1 = pd.merge(j0, s3, on="Cust_id", how="inner")
j2 = pd.merge(j1, s2, on="Ord_id", how="inner")

result = j2[["Order_Quantity", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]].copy()

result["Order_Quantity"] = result["Order_Quantity"].astype(int)
result["Sales"] = result["Sales"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)