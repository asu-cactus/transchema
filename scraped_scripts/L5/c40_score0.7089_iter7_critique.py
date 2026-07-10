import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join source1 with source0 on Cust_id
df = pd.merge(source1, source0, on="Cust_id", how="inner")

# Join with source3 on Prod_id
df = pd.merge(df, source3, on="Prod_id", how="inner")

# Join with source2 on Ord_id
df = pd.merge(df, source2, on="Ord_id", how="inner")

# Join with source4 on Ship_id
df = pd.merge(df, source4, on="Ship_id", how="inner")

# Select columns as per target schema
result = df[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]].copy()

# Convert Ord_id, Prod_id, Cust_id from strings like 'Ord_1082' to integers 1082
result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r'(\d+)').astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r'(\d+)').astype(int)

# Group by all target columns to ensure uniqueness (no aggregation needed)
result = result.drop_duplicates(subset=["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)