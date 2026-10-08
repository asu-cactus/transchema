import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)

merged = pd.merge(source1, source0, on="Cust_id", how="inner")

result = merged[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]].copy()

result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "").astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "").astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "").astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)