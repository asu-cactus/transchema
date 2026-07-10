import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

# Join source3 and source4 on Ship_id
df = pd.merge(source3, source4, on="Ship_id", how="inner")

# Join with source1 on Ord_id
df = pd.merge(df, source1, on="Ord_id", how="inner")

# Join with source2 on Cust_id
df = pd.merge(df, source2, on="Cust_id", how="inner")

# Select columns as per target schema
result = df[["Ship_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]].copy()

# Convert Ord_id, Prod_id, Ship_id, Cust_id from string IDs like 'Ord_1' to integer IDs by extracting the numeric part
result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r'(\d+)').astype(int)
result["Ship_id"] = result["Ship_id"].str.extract(r'(\d+)').astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r'(\d+)').astype(int)

# Group by all columns to remove duplicates and match target row count
result = result.groupby(["Ship_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"], as_index=False).size()

# The groupby.size() returns a Series with name 'size', we only want the grouped keys, so drop the size column
result = result.drop(columns=["size"])

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)