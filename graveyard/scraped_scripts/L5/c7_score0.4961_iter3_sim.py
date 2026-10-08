import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

r = pd.merge(s4, s3, on="Ship_id")
r = pd.merge(r, s0, on="Prod_id")
r = pd.merge(r, s1, on="Cust_id")
r = pd.merge(r, s2, on="Ord_id")

r = r[["Product_Sub_Category", "Order_Quantity", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

r.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)