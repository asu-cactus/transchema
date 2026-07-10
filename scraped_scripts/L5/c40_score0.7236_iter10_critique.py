import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

# Join s1 and s4 on Ship_id
j1 = pd.merge(s1, s4, on="Ship_id")

# Join with s2 on Ord_id
j2 = pd.merge(j1, s2, on="Ord_id")

# Join with s0 on Cust_id
j3 = pd.merge(j2, s0, on="Cust_id")

# Join with s3 on Prod_id
j4 = pd.merge(j3, s3, on="Prod_id")

# Convert Ord_id, Prod_id, Cust_id from strings like "Ord_1082" to integers 1082
j4["Ord_id"] = j4["Ord_id"].str.extract(r'(\d+)').astype(int)
j4["Prod_id"] = j4["Prod_id"].str.extract(r'(\d+)').astype(int)
j4["Cust_id"] = j4["Cust_id"].str.extract(r'(\d+)').astype(int)

# Select and reorder columns as per target schema
result = j4[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]]

# Group by all columns to remove duplicates (if any)
result = result.drop_duplicates()

# Write to output CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)