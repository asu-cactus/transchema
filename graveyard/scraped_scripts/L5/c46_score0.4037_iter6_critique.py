import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join Source5_46_4 and Source5_46_3 on Prod_id
j1 = pd.merge(s4, s3, on="Prod_id", how="inner")

# Join with Source5_46_0 on Cust_id
j2 = pd.merge(j1, s0, on="Cust_id", how="inner")

# Join with Source5_46_2 on Ord_id
j3 = pd.merge(j2, s2, on="Ord_id", how="inner")

# Join with Source5_46_1 on Ship_id
j4 = pd.merge(j3, s1, on="Ship_id", how="inner")

# Select target columns
result = j4[["Customer_Name", "Ord_id", "Prod_id", "Ship_id"]].copy()

# Convert Ord_id, Prod_id, Ship_id to integers by stripping prefixes
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
result["Ship_id"] = result["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)

# Drop duplicates to ensure uniqueness as in target examples
result = result.drop_duplicates(subset=["Customer_Name", "Ord_id", "Prod_id", "Ship_id"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)