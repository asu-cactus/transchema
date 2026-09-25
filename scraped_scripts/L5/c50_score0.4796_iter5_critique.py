import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

# Join fact table with orders on Ord_id
j1 = pd.merge(s4, s1, on="Ord_id", how="inner")

# Join with shipping info on Ship_id
j2 = pd.merge(j1, s0, on="Ship_id", how="inner")

# Join with product info on Prod_id
j3 = pd.merge(j2, s2, on="Prod_id", how="inner")

# Join with customer info on Cust_id
j4 = pd.merge(j3, s3, on="Cust_id", how="inner")

# Select target columns
result = j4[["Ship_Date", "Ord_id", "Prod_id", "Ship_id"]].copy()

# Convert IDs from strings like "Ord_1082" to integers
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
result["Ship_id"] = result["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)

# Group by all target columns to remove duplicates (no aggregation needed)
result = result.drop_duplicates(subset=["Ship_Date", "Ord_id", "Prod_id", "Ship_id"])

# Ensure Ship_Date is string type
result["Ship_Date"] = result["Ship_Date"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)