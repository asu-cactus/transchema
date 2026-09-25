import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Join tables on keys
j0 = pd.merge(s2, s0, on="Cust_id", how="inner")
j1 = pd.merge(j0, s3, on="Prod_id", how="inner")
j2 = pd.merge(j1, s4, on="Ord_id", how="inner")
j3 = pd.merge(j2, s1, on="Ship_id", how="inner")

# Select only the target columns
result = j3[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]]

# Convert Ord_id, Prod_id, Cust_id from strings like "Ord_1082" to integers 1082
result["Ord_id"] = result["Ord_id"].str.extract(r"(\d+)").astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r"(\d+)").astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r"(\d+)").astype(int)

# Group by all four columns to remove duplicates (if any)
result = result.drop_duplicates(subset=["Ship_id", "Ord_id", "Prod_id", "Cust_id"])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)