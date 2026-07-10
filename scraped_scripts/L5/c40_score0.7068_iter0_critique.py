import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join Source1 and Source0 on Cust_id
merged = pd.merge(source1, source0, on="Cust_id", how="inner")

# Join with Source2 on Ord_id
merged = pd.merge(merged, source2, on="Ord_id", how="inner")

# Join with Source3 on Prod_id
merged = pd.merge(merged, source3, on="Prod_id", how="inner")

# Join with Source4 on Ship_id
merged = pd.merge(merged, source4, on="Ship_id", how="inner")

# Select required columns for target schema
result = merged[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]].copy()

# Convert Ord_id, Prod_id, Cust_id to integers by stripping prefixes
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)