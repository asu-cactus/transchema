import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

j1 = pd.merge(s1, s2, on="Cust_id", how="inner")
j2 = pd.merge(j1, s3, on="Prod_id", how="inner")
j3 = pd.merge(j2, s4, on="Ship_id", how="inner")
j4 = pd.merge(j3, s0, on="Ord_id", how="inner")

result = j4[["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

result["Ord_id"] = result["Ord_id"].astype(str)
result["Prod_id"] = result["Prod_id"].astype(str)
result["Ship_id"] = result["Ship_id"].astype(str)
result["Cust_id"] = result["Cust_id"].astype(str)
result["Product_Sub_Category"] = result["Product_Sub_Category"].astype(str)
result["Sales"] = pd.to_numeric(result["Sales"], errors='coerce').fillna(0).astype(int)
result["Discount"] = pd.to_numeric(result["Discount"], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)