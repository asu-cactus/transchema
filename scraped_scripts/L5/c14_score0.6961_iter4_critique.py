import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Join Source2 and Source1 on Ship_id
join_21 = pd.merge(source2, source1, on="Ship_id", how="inner")

# Join with Source0 on Cust_id
join_210 = pd.merge(join_21, source0, on="Cust_id", how="inner")

# Join with Source4 on Ord_id
join_2104 = pd.merge(join_210, source4, on="Ord_id", how="inner")

# Join with Source3 on Prod_id
join_all = pd.merge(join_2104, source3, on="Prod_id", how="inner")

# Extract required columns
result = join_all[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]].copy()

# Convert Ord_id, Prod_id, Cust_id from strings to integers
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Remove duplicates by grouping on all four columns (no aggregation needed)
result = result.drop_duplicates(subset=["Ship_id", "Ord_id", "Prod_id", "Cust_id"])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)