import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

# Join Source1 and Source2 on Ship_id
j0 = pd.merge(s1, s2, on="Ship_id", how="inner")

# Join with Source0 on Prod_id
j1 = pd.merge(j0, s0, on="Prod_id", how="inner")

# Join with Source3 on Cust_id
j2 = pd.merge(j1, s3, on="Cust_id", how="inner")

# Join with Source4 on Ord_id
j3 = pd.merge(j2, s4, on="Ord_id", how="inner")

# Convert string IDs to integers as per target schema
j3["Ship_id"] = j3["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
j3["Ord_id"] = j3["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
j3["Cust_id"] = j3["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Select relevant columns including Prod_id from Source2 (already in j3)
result = j3[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]]

# Group by all target columns to remove duplicates and match target row count
result = result.groupby(["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"], as_index=False).size()

# Drop the 'size' column created by groupby.size()
result = result.drop(columns=["size"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)