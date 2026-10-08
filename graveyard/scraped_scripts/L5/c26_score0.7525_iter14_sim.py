import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

j1 = pd.merge(s1, s2, on="Ord_id", how="inner")
j2 = pd.merge(j1, s4, on="Prod_id", how="inner")
j3 = pd.merge(j2, s0, on="Ship_id", how="inner")
j4 = pd.merge(j3, s3, on="Cust_id", how="inner")

result = j4[["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)