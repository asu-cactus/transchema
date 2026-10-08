import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="Cust_id", how="inner")

result = pd.DataFrame()
result["Ship_id"] = merged["Ship_id"]
result["Customer_Name"] = merged["Customer_Name"]
result["Ord_id"] = merged["Ord_id"].str.replace("Ord_", "").astype(int)
result["Prod_id"] = merged["Prod_id"].str.replace("Prod_", "").astype(int)
result["Cust_id"] = merged["Cust_id"].str.replace("Cust_", "").astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)